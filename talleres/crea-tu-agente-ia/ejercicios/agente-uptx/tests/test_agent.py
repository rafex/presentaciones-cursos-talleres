"""Pruebas del loop de tools usando un cliente falso, sin consumir Groq."""

from types import SimpleNamespace

from main import ejecutar_agente
from tools import TOOLS, FUNCTIONS


class FakeCompletions:
    """Simula primero una llamada a tool y después una respuesta final."""

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
    """Expone la misma ruta de atributos que usa el SDK de OpenAI."""

    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions())


def test_agent_uses_required_then_auto_and_returns_text() -> None:
    """El runtime exige una tool al inicio y luego permite texto final."""

    client = FakeClient()
    answer = ejecutar_agente("¿Qué carreras ofrece la UPTx?", client=client)
    calls = client.chat.completions.calls

    assert "Mecatrónica" in answer
    assert calls[0]["tool_choice"] == "required"
    assert calls[1]["tool_choice"] == "auto"
    assert calls[1]["messages"][-1]["role"] == "tool"


def test_source_tool_is_exposed_to_the_model() -> None:
    """La tool de navegación aparece en el schema y en el dispatcher."""

    names = {item["function"]["name"] for item in TOOLS}
    assert "consultar_fuente_uptx" in names
    assert "consultar_fuente_uptx" in FUNCTIONS
