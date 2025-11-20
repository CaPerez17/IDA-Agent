# Prompt para Figma Make - Presentación Visual IDA Agent

## 🎯 OBJETIVO
Crear un sitio web interactivo en Figma que sirva como presentación visual para la sustentación técnica del Félix Intent Disambiguation Agent (IDA). El diseño debe ser profesional, claro, y altamente intuitivo para explicar la arquitectura y funcionamiento del sistema.

---

## 📐 ESTRUCTURA DEL SITIO (4 Páginas Principales)

### **PÁGINA 1: OVERALL ARCHITECTURE (Arquitectura General)**

**Título Principal**: "Félix IDA - Arquitectura General"

**Contenido a Visualizar**:

1. **Diagrama de Alto Nivel** (Centro de la página):
   ```
   [Usuario] 
      ↓
   [IDA Agent (ADK)]
      ↓
   [Intent Disambiguation Tool]
      ↓
   [Mock Classifier] → [State Manager] → [Response Generator]
      ↓
   [Output: route_to intent_id]
   ```

2. **Componentes Principales** (Cards con iconos):
   - **`ida_agent`** (agent.py)
     - Tipo: Google ADK Agent
     - Modelo: gemini-2.0-flash-exp
     - Responsabilidad: Orquestación de conversación
   
   - **`intent_disambiguation_tool`** (tools.py)
     - Tipo: FunctionTool
     - Responsabilidad: Lógica de negocio principal
     - Maneja: State machine (initial → awaiting → resolved)
   
   - **`simple_classifier`** (classifier.py)
     - Tipo: Mock Classifier
     - Scoring: Keywords (50%) + Triggers (30%) + Semantic (20%)
     - Sin APIs externas, todo local
   
   - **`IdaState`** (state.py)
     - Tipo: Dataclass
     - Campos: phase, candidate_intents, selected_intent_id
     - Persiste entre turnos de conversación

3. **Stack Tecnológico** (Badge style):
   - Google ADK Framework
   - Python 3.12+
   - Mock Logic (sin ML, sin APIs)
   - Self-contained

**Diseño Visual**:
- Fondo: Gradiente sutil azul/gris profesional
- Cards: Sombras suaves, bordes redondeados
- Colores: Azul primario (#2563EB), Gris texto (#374151)
- Tipografía: Sans-serif moderna (Inter o similar)

---

### **PÁGINA 2: ADK STRUCTURE (Estructura dentro de ADK)**

**Título Principal**: "Cómo Estructuramos los Pasos dentro de ADK"

**Contenido a Visualizar**:

1. **Flujo ADK Estándar** (Diagrama de flujo horizontal):
   ```
   User Message
      ↓
   ADK Agent (ida_agent)
      ↓
   Agent decides to call tool
      ↓
   FunctionTool (intent_disambiguation_tool)
      ↓
   Tool executes business logic
      ↓
   Tool returns structured dict
      ↓
   Agent formats response to user
   ```

2. **Código Clave** (Code blocks con syntax highlighting):
   
   **Agent Definition** (agent.py):
   ```python
   ida_agent = Agent(
       name="felix_intent_disambiguation_agent",
       model="gemini-2.0-flash-exp",
       tools=[intent_disambiguation_tool],
       instruction="...disambiguation layer..."
   )
   ```
   
   **Tool Definition** (tools.py):
   ```python
   intent_disambiguation_tool = FunctionTool(
       func=intent_disambiguation_function
   )
   ```

3. **Por qué esta Estructura**:
   - ✅ Un solo Agent (requisito del PDF)
   - ✅ FunctionTool contiene toda la lógica de negocio
   - ✅ No custom routers fuera del flow model de ADK
   - ✅ State se pasa como parámetro (patrón ADK estándar)

4. **Ventajas del Diseño**:
   - Modular: Cada componente tiene responsabilidad única
   - Testeable: Funciones puras, fácil de mockear
   - Escalable: Fácil agregar nuevos intents o modos

**Diseño Visual**:
- Diagrama de flujo con flechas animadas (si es posible)
- Code blocks con fondo oscuro (#1F2937) y texto verde claro
- Cards explicativas con iconos de checkmark verde

---

### **PÁGINA 3: STATE MACHINE & FLOW (Manejo de Ambiguidad y Estado)**

**Título Principal**: "Cómo Maneja Ambiguidad, Clarificación y Routing"

**Contenido a Visualizar**:

1. **State Machine Diagram** (Diagrama de estados grande):
   ```
   ┌─────────┐
   │ initial │
   └────┬────┘
        │
        ├─[High Confidence]──→ ┌──────────┐
        │                      │ resolved │
        │                      └──────────┘
        │
        └─[Ambiguous]──→ ┌──────────────────────┐
                         │ awaiting_clarification│
                         └────┬───────────────────┘
                              │
                              └─[User Clarifies]──→ ┌──────────┐
                                                    │ resolved │
                                                    └──────────┘
   ```

2. **Proceso Detallado** (Timeline vertical):

   **Paso 1: Detección de Ambiguidad**
   - Usuario envía mensaje: "I want to handle my money"
   - Classifier calcula scores para todos los intents
   - Top 3 candidatos: send_money (0.45), check_balance (0.42), pay_bill (0.20)
   - **Detección**: |0.45 - 0.42| = 0.03 < 0.15 (CONFIDENCE_MARGIN)
   - **Decisión**: AMBIGUO → Pausar procesamiento

   **Paso 2: Solicitar Clarificación**
   - Estado actualiza: `phase = "awaiting_clarification"`
   - Guarda: `candidate_intents = [top 3]`
   - Retorna: `{"status": "NEED_CLARIFICATION", "options": [...]}`
   - Usuario ve: "I'm not sure what you meant. Options: Send Money, Check Balance, Pay Bill"

   **Paso 3: Resolver Clarificación**
   - Usuario responde: "send money to mom"
   - `resolve_clarification()` busca keywords: "send", "money" → match con `send_money`
   - Estado actualiza: `phase = "resolved"`, `selected_intent_id = "send_money"`
   - Retorna: `{"status": "RESOLVED", "route_to": "send_money"}`

   **Paso 4: Handoff**
   - Output estructurado listo para downstream agent
   - Campo `route_to` indica claramente el intent seleccionado

3. **Código del State Machine** (Snippet clave):
   ```python
   if state.phase == "initial":
       candidates = simple_classifier(user_message, intents)
       if is_ambiguous(top, second):
           state.phase = "awaiting_clarification"
           return {"status": "NEED_CLARIFICATION", "options": [...]}
   
   elif state.phase == "awaiting_clarification":
       selected_id = resolve_clarification(user_message, state.candidate_intents)
       state.phase = "resolved"
       return {"status": "RESOLVED", "route_to": selected_id}
   ```

4. **Mantenimiento de Estado** (Visualización):
   - **Antes de clarificación**: `IdaState(phase="initial", candidate_intents=[])`
   - **Durante clarificación**: `IdaState(phase="awaiting_clarification", candidate_intents=[...])`
   - **Después de resolución**: `IdaState(phase="resolved", selected_intent_id="send_money")`
   - **Mismo objeto** se pasa entre llamadas, manteniendo referencia

**Diseño Visual**:
- State machine con círculos conectados por flechas
- Timeline con números de paso (1, 2, 3, 4)
- Code snippets con resaltado de sintaxis
- Cards de estado con colores diferentes (azul=initial, amarillo=awaiting, verde=resolved)

---

### **PÁGINA 4: LIVE DEMO (Ejemplo Interactivo)**

**Título Principal**: "Ejemplo de Interacción en Vivo"

**Contenido a Visualizar**:

1. **Conversación Completa** (Chat-style interface):

   **Turno 1 - Mensaje Ambiguo**:
   ```
   👤 Usuario: "I want to handle my money"
   
   🤖 Agent: "I'm not sure what you meant. Can you clarify your intent?"
   
   📋 Opciones Presentadas:
   1. Send Money (Score: 0.45)
   2. Check Balance (Score: 0.42)
   3. Pay Bill (Score: 0.20)
   
   ⚠️ Razón de Ambigüedad: Score difference < 0.15
   ```

   **Turno 2 - Clarificación**:
   ```
   👤 Usuario: "send money to mom"
   
   🔍 Proceso Interno:
   - Keyword match: "send" + "money" → send_money
   - Resolved using resolve_clarification()
   
   🤖 Agent: "Thanks! I will route you to send_money."
   
   ✅ Estado Final:
   - phase: "resolved"
   - selected_intent_id: "send_money"
   - route_to: "send_money"
   ```

2. **Ejemplo 2 - Resolución Directa** (Sin Clarificación):
   ```
   👤 Usuario: "check my account balance"
   
   🔍 Proceso Interno:
   - Classifier scores: check_balance (0.85), send_money (0.20)
   - Confidence: 0.85 > 0.30 ✓
   - Margin: |0.85 - 0.20| = 0.65 > 0.15 ✓
   - Decisión: NO AMBIGUO → Resolver directamente
   
   🤖 Agent: "Great, I will help you with check balance."
   
   ✅ Estado Final:
   - phase: "resolved"
   - selected_intent_id: "check_balance"
   ```

3. **Métricas del Mock Classifier** (Tabla):
   | Componente | Peso | Ejemplo Score |
   |------------|------|---------------|
   | Keywords | 50% | 0.40 (2/5 keywords found) |
   | Triggers | 30% | 0.50 (1/2 regex matched) |
   | Semantic | 20% | 0.81 (cosine similarity) |
   | **Final** | **100%** | **0.567** |

4. **Botón CTA**: "Ver Demo Interactivo" (link a `interactive_demo.py` o video)

**Diseño Visual**:
- Chat bubbles estilo WhatsApp/iMessage
- Usuario: Burbujas azules a la derecha
- Agent: Burbujas grises a la izquierda
- Cards de "proceso interno" con fondo amarillo claro
- Tabla de métricas con bordes y alternancia de colores
- Animación sutil de aparición de mensajes (si es posible)

---

## 🎨 ESPECIFICACIONES DE DISEÑO GENERALES

### **Paleta de Colores**:
- **Primario**: #2563EB (Azul profesional)
- **Secundario**: #10B981 (Verde éxito)
- **Advertencia**: #F59E0B (Amarillo ambigüedad)
- **Texto Principal**: #111827 (Gris oscuro)
- **Texto Secundario**: #6B7280 (Gris medio)
- **Fondo**: #F9FAFB (Gris muy claro)
- **Cards**: #FFFFFF (Blanco)

### **Tipografía**:
- **Títulos**: Bold, 32-48px, Inter o Poppins
- **Subtítulos**: SemiBold, 24-32px
- **Cuerpo**: Regular, 16-18px, Inter
- **Código**: Mono, 14px, Fira Code o JetBrains Mono

### **Espaciado**:
- Padding entre secciones: 64px
- Padding dentro de cards: 24px
- Gap entre elementos: 16px
- Border radius: 8-12px

### **Elementos Interactivos**:
- Hover effects en cards (elevación sutil)
- Transiciones suaves (0.2s ease)
- Scroll indicators si hay múltiples secciones
- Navigation bar fija en la parte superior

---

## 📱 RESPONSIVE DESIGN

- **Desktop**: Layout de 2-3 columnas donde sea apropiado
- **Tablet**: Layout de 1-2 columnas
- **Mobile**: Stack vertical, texto legible, código con scroll horizontal

---

## 🔗 ELEMENTOS ADICIONALES A INCLUIR

1. **Header/Navigation**:
   - Logo o nombre del proyecto: "Félix IDA"
   - Links a las 4 páginas principales
   - Botón "Ver Código" (link a GitHub)

2. **Footer**:
   - "Built with Google ADK"
   - Link al repositorio GitHub
   - Información del autor

3. **Call-to-Actions**:
   - "Ver Demo en GitHub" (link al repo)
   - "Ejecutar Demo Local" (instrucciones)
   - "Ver Documentación Completa" (link a README)

---

## 📝 INSTRUCCIONES ESPECÍFICAS PARA FIGMA MAKE

1. **Crear 4 frames principales** (uno por página)
2. **Usar componentes reutilizables** para cards, code blocks, y diagramas
3. **Aplicar el sistema de diseño** con la paleta y tipografía especificadas
4. **Agregar interacciones** entre páginas (prototipo de navegación)
5. **Incluir placeholders** para código que luego se puede reemplazar con screenshots reales
6. **Optimizar para presentación** (modo presentación de Figma)

---

## ✅ CHECKLIST DE CONTENIDO

- [ ] Página 1: Arquitectura general con diagrama de alto nivel
- [ ] Página 2: Estructura ADK con código y explicación
- [ ] Página 3: State machine con timeline del proceso
- [ ] Página 4: Ejemplo interactivo con conversación completa
- [ ] Navigation bar funcional
- [ ] Footer con links
- [ ] Responsive design aplicado
- [ ] Paleta de colores consistente
- [ ] Tipografía legible y profesional
- [ ] Elementos interactivos (hover, transiciones)

---

**NOTA FINAL**: Este prompt está diseñado para que Figma Make pueda generar un sitio completo y profesional que cubra todos los puntos requeridos en la entrevista técnica. El diseño debe ser visualmente atractivo pero también informativo y técnicamente preciso.

