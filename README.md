# Interactive Recipes with AG-UI Protocol

Una aplicación de recetas interactivas usando Microsoft Agent Framework (Python) y Reflex como frontend, comunicándose mediante el protocolo AG-UI.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Reflex)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ RecipeCard  │  │   Chat      │  │   Ingredients Badge     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │ RecipeState │ (Reflex State)               │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │ AG-UI Client│ (SSE Consumer)               │
│                    └──────┬──────┘                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP POST + SSE (AG-UI Events)
┌───────────────────────────┼─────────────────────────────────────┐
│                           │            BACKEND (FastAPI)        │
│                    ┌──────┴──────┐                              │
│                    │ AG-UI Adapter│                             │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │ Recipe Agent│ (Microsoft Agent Framework)  │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │  OpenAI LLM │                              │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
testag-ui/
├── backend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── main.py              # FastAPI server + AG-UI endpoints
│   └── agents/
│       └── recipe_agent.py  # Microsoft Agent Framework agent
│
├── frontend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── rxconfig.py          # Reflex configuration
│   ├── recipe_app/
│   │   ├── __init__.py
│   │   ├── recipe_app.py    # Main Reflex app
│   │   ├── state.py         # RecipeState with AG-UI handling
│   │   ├── ag_ui_client.py  # AG-UI SSE client
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── recipe_card.py
│   │       ├── chat.py
│   │       └── ingredients.py
│   └── assets/
│
└── README.md
```

## 🚀 Inicio Rápido

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -e .

# Configurar variables de entorno
copy .env.example .env
# Edita .env con tu API key de OpenAI

# Ejecutar servidor
uvicorn main:app --reload --port 8888
```

### 2. Frontend

```bash
cd frontend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -e .

# Configurar variables de entorno
copy .env.example .env

# Inicializar Reflex
reflex init

# Ejecutar frontend
reflex run
```

## 🔌 Protocolo AG-UI

El protocolo AG-UI define eventos para comunicación agente-UI:

| Evento | Descripción |
|--------|-------------|
| `RUN_STARTED` | Inicio de ejecución del agente |
| `TEXT_MESSAGE_START` | Inicio de mensaje de texto |
| `TEXT_MESSAGE_CONTENT` | Contenido del mensaje (streaming) |
| `TEXT_MESSAGE_END` | Fin del mensaje |
| `STATE_SNAPSHOT` | Estado completo (receta, ingredientes) |
| `STATE_DELTA` | Cambio parcial del estado |
| `TOOL_CALL_START` | Inicio de llamada a herramienta |
| `TOOL_CALL_END` | Fin de llamada a herramienta |
| `RUN_FINISHED` | Fin de ejecución |

## 🎯 Características

- ✅ Generación de recetas con IA
- ✅ Streaming de respuestas en tiempo real
- ✅ Estado compartido (shared state) entre agente y UI
- ✅ Actualización incremental de ingredientes
- ✅ Interfaz moderna y responsiva con Reflex
- ✅ 100% Python (backend y frontend)

## 📝 Licencia

MIT
