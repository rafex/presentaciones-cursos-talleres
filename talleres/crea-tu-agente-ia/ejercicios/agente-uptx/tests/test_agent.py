from types import SimpleNamespace

from main import ejecutar_agente


class FakeCompletions:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            message = SimpleNamespace(
                content=None,
                tool_calls=[
                    SimpleNamespace(
                        id="call-1",
                        function=SimpleNamespace(
                            name="consultar_uptx",
                            arguments='{"pregunta":"¿Qué carreras ofrece la UPTx?"}',
                        ),
                    )
                ],
            )
        else:
            message = SimpleNamespace(
                content="La UPTx ofrece Ingeniería Mecatrónica y otras carreras.",
                tool_calls=None,
            )
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions())


def test_agent_uses_required_then_auto_and_returns_text() -> None:
    client = FakeClient()
    answer = ejecutar_agente("¿Qué carreras ofrece la UPTx?", client=client)
    calls = client.chat.completions.calls

    assert "Mecatrónica" in answer
    assert calls[0]["tool_choice"] == "required"
    assert calls[1]["tool_choice"] == "auto"
    assert calls[1]["messages"][-1]["role"] == "tool"
