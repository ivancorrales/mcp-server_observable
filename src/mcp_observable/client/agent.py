import asyncio
import os
import time
from dataclasses import dataclass, field

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

OLLAMA = os.getenv('OLLAMA_URL', 'http://localhost:11434')
MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1')
MCP_URL = os.getenv('MCP_URL', 'http://localhost:8000/mcp')
API_KEY = os.getenv('MCP_API_KEY', 'dev-key-123')

# Precio de referencia en USD por millón de tokens (ajústalo al proveedor que quieras comparar)
PRICE_IN, PRICE_OUT = 3.0, 15.0

SYSTEM = (
    'Eres un analista de datos de una tienda online. '
    'Usa siempre las herramientas disponibles para responder con datos reales y no inventes cifras.'
)




@dataclass
class RunResult:
    answer: str = ''
    tools_called: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    seconds: float = 0.0


async def chat(http: httpx.AsyncClient, messages: list, tools: list, result: RunResult) -> dict:
    with tracer.start_as_current_span('llm.call') as span:
        t0 = time.perf_counter()
        resp = await http.post(
            f'{OLLAMA}/api/chat',
            json={'model': MODEL, 'messages': messages, 'tools': tools, 'stream': False},
        )
        resp.raise_for_status()
        data = resp.json()

        tok_in = data.get('prompt_eval_count', 0)
        tok_out = data.get('eval_count', 0)
        usd = tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT
        ms = (time.perf_counter() - t0) * 1000

        tokens_c.add(tok_in, {'model': MODEL, 'type': 'input'})
        tokens_c.add(tok_out, {'model': MODEL, 'type': 'output'})
        cost_c.add(usd, {'model': MODEL})
        llm_latency.record(ms, {'model': MODEL})

        result.tokens_in += tok_in
        result.tokens_out += tok_out
        result.cost_usd += usd

        span.set_attribute('llm.model', MODEL)
        span.set_attribute('llm.tokens.input', tok_in)
        span.set_attribute('llm.tokens.output', tok_out)
        span.set_attribute('llm.cost_usd', usd)
        return data['message']


async def run(question: str) -> RunResult:
    result = RunResult()
    start = time.perf_counter()
    with tracer.start_as_current_span('agent.run') as span:
        span.set_attribute('agent.question', question[:200])
        headers = {'x-api-key': API_KEY}
        propagate.inject(headers)  # añade traceparent para enlazar cliente y servidor

        async with httpx.AsyncClient(timeout=120) as http, \
                streamablehttp_client(MCP_URL, headers=headers) as (read, write, _), \
                ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            tools = [
                {
                    'type': 'function',
                    'function': {
                        'name': t.name,
                        'description': t.description or '',
                        'parameters': t.inputSchema,
                    },
                }
                for t in listed.tools
            ]
            messages = [
                {'role': 'system', 'content': SYSTEM},
                {'role': 'user', 'content': question},
            ]
            for _ in range(6):
                msg = await chat(http, messages, tools, result)
                messages.append(msg)
                tool_calls = msg.get('tool_calls') or []
                if not tool_calls:
                    result.answer = msg.get('content', '')
                    break
                for call in tool_calls:
                    fn = call['function']
                    result.tools_called.append(fn['name'])
                    res = await session.call_tool(fn['name'], fn['arguments'])
                    text = ''.join(b.text for b in res.content if b.type == 'text')
                    messages.append({'role': 'tool', 'tool_name': fn['name'], 'content': text})
            else:
                result.answer = 'Límite de iteraciones alcanzado'

        span.set_attribute('agent.tools_called', ','.join(result.tools_called))
        span.set_attribute('agent.cost_usd', result.cost_usd)
    result.seconds = time.perf_counter() - start
    return result


def flush_telemetry() -> None:
    trace.get_tracer_provider().shutdown()
    metrics.get_meter_provider().shutdown()


if __name__ == '__main__':
    r = asyncio.run(run('¿Cuáles son los 3 productos que más facturan y cuánto facturamos en 2026?'))
    print(r.answer)
    print(
        f'herramientas={r.tools_called} tokens={r.tokens_in}+{r.tokens_out} '
        f'coste=${r.cost_usd:.5f} tiempo={r.seconds:.1f}s'
    )
    flush_telemetry()  # vacía los buffers de telemetría antes de salir