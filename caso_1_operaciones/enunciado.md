# Caso técnico: sistema de análisis inteligente para operaciones Rappi

**Rol:** AI Engineer  

**Tiempo para la entrega:** 2 días calendario  

**Formato de presentación:** 30 minutos (20 min presentación + 10 min Q&A)

---

## 1. Contexto del problema

Rappi opera en 9 países con cientos de zonas geográficas, cada una con sus propias dinámicas operacionales. Los equipos de Strategy, Planning & Analytics (SP&A) y Operations necesitan tomar decisiones basadas en datos de forma continua, pero enfrentan dos desafíos principales:

1. **Acceso fragmentado a insights:** los datos existen, pero hace falta conocimiento técnico (SQL, Python) para obtener respuestas a preguntas de negocio.
2. **Análisis manual repetitivo:** cada semana los equipos dedican horas a identificar zonas con problemas, oportunidades de crecimiento y anomalías operacionales.

**Tu misión** es construir un sistema basado en IA que democratice el acceso a estos datos y automatice la generación de insights accionables.

---

## 2. Entregables requeridos

### 2.1 Bot conversacional de datos (70% del peso)

Desarrolla un chatbot que permita a usuarios no técnicos hacer preguntas en lenguaje natural sobre las métricas operacionales y recibir respuestas precisas.

**Requisitos mínimos**

- **Capacidad de respuesta a consultas complejas** (al menos estos casos de uso):
  - **Filtrado:** «¿Cuáles son las 5 zonas con mayor % Lead Penetration esta semana?»
  - **Comparaciones:** «Compara el Perfect Order entre zonas Wealthy y Non Wealthy en México»
  - **Tendencias temporales:** «Muestra la evolución de Gross Profit UE en Chapinero últimas 8 semanas»
  - **Agregaciones:** «¿Cuál es el promedio de Lead Penetration por país?»
  - **Análisis multivariable:** «¿Qué zonas tienen alto Lead Penetration pero bajo Perfect Order?»
  - **Inferencia:** «¿Cuáles son las zonas que más crecen en órdenes en las últimas 5 semanas y qué podría explicar el crecimiento?»
- **Manejo de contexto:** el bot debe entender el contexto de negocio (ej.: si preguntan por «zonas problemáticas», inferir métricas deterioradas).
- **Sugerencias** proactivas de análisis.
- **Memoria conversacional** (seguimiento del diálogo).

**Bonus (no obligatorio)**

- **Visualización:** gráficos cuando la pregunta lo amerite (líneas para tendencias, barras para comparaciones, etc.)
- Exportación de resultados (CSV, PDF)

### 2.2 Sistema de insights automáticos (30% del peso)

Construye un sistema que analice automáticamente los datos y genere un reporte ejecutivo con los insights más relevantes.

**Requisitos mínimos**

- **Identificación automática de insights** en al menos estas categorías:
  - **Anomalías:** zonas con cambios fuertes semana a semana (>10% deterioro o mejora)
  - **Tendencias preocupantes:** métricas en deterioro consistente (3+ semanas seguidas)
  - **Benchmarking:** comparación de zonas similares (mismo país/tipo) con desempeño divergente
  - **Correlaciones:** relaciones entre métricas (ej.: zonas con bajo Lead Penetration y baja conversión)
  - Oportunidades en general
- **Reporte ejecutivo estructurado** que incluya:
  - Resumen ejecutivo (top 3–5 hallazgos críticos)
  - Detalle por categoría de insight
  - Recomendaciones accionables por hallazgo
- **Formato de salida:** Markdown, HTML o PDF (elige el más apropiado)

**Bonus (no obligatorio)**

- Envío automático por email

---

## 3. Datos proporcionados

Recibirás **2 datasets** en formato CSV.

### Dataset 1: métricas input (métricas operacionales por zona)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `COUNTRY` | string | Código de país (AR, BR, CL, CO, CR, EC, MX, PE, UY) |
| `CITY` | string | Nombre de la ciudad |
| `ZONE` | string | Zona operacional o barrio |
| `ZONE_TYPE` | string | Segmentación por riqueza (Wealthy / Non Wealthy) |
| `ZONE_PRIORITIZATION` | string | Priorización estratégica (High Priority / Prioritized / Not Prioritized) |
| `METRIC` | string | Nombre de la métrica medida |
| `L8W_VALUE` … `L0W_VALUE` | float | Valor de la métrica en cada una de las últimas 8 semanas (L8W = hace 8 semanas, L0W = semana actual) |

### Dataset 2: órdenes (volumen de órdenes por zona)

| Columna | Descripción |
|---------|-------------|
| `COUNTRY`, `CITY`, `ZONE` | Identificadores geográficos |
| `METRIC` | Siempre «Orders» |
| `L8W` … `L0W` | Número de órdenes en cada semana |

### Diccionario de métricas

| Métrica | Descripción |
|---------|-------------|
| **% PRO Users Who Breakeven** | Usuarios con suscripción Pro cuyo valor generado para la empresa (compras, comisiones, etc.) ha cubierto el costo total de su membresía / total de usuarios con suscripción Pro |
| **% Restaurants Sessions With Optimal Assortment** | Sesiones con un mínimo de 40 restaurantes / total de sesiones |
| **Gross Profit UE** | Margen bruto de ganancia / total de órdenes |
| **Lead Penetration** | Tiendas habilitadas en Rappi / (tiendas identificadas como prospectos (leads) + tiendas habilitadas + tiendas que salieron de Rappi) |
| **MLTV Top Verticals Adoption** | Usuarios con órdenes en distintas verticales (restaurantes, super, pharmacy, liquors) / total usuarios |
| **Non-Pro PTC → OP** | Conversión de usuarios No Pro de «Proceed to Checkout» a «Order Placed» |
| **Perfect Orders** | Órdenes sin cancelaciones, defectos ni demora / total de órdenes |
| **Pro Adoption** | Usuarios con suscripción Pro / total usuarios de Rappi |
| **Restaurants Markdowns / GMV** | Descuentos totales en órdenes de restaurantes / GMV restaurantes |
| **Restaurants SS → ATC CVR** | Conversión en restaurantes de «Select Store» a «Add to Cart» |
| **Restaurants SST → SS CVR** | Usuarios que, tras seleccionar «Restaurantes» o «Supermercados», eligen una tienda concreta de la lista |
| **Retail SST → SS CVR** | Igual que la anterior, partiendo de la selección de supermercados |
| **Turbo Adoption** | Usuarios que compran en Turbo (fast de Rappi) / usuarios de Rappi con tiendas Turbo disponibles |

---

## 4. Requisitos técnicos

### Stack tecnológico

**Libertad total de herramientas**

- **LLMs:** OpenAI (GPT-4, GPT-3.5), Anthropic (Claude), Google (Gemini), modelos open source (Llama, Mistral), etc.
- **Plataformas no-code/low-code:** Make, n8n, Zapier, etc.
- **Lenguajes:** Python, JavaScript, TypeScript u otros
- **Frameworks:** Streamlit, Gradio, Flask, FastAPI, Next.js, React, etc.

Si usas APIs de pago, **documenta el costo estimado** por uso (ej.: ~USD 0.50 por sesión de 10 preguntas).

### Código y reproducibilidad

- Incluye un **README** con instrucciones claras de cómo funciona tu solución.
- **Organización:** estructura el proyecto de la forma que consideres más clara.

**Nota:** si usas Make, n8n u otras plataformas, exporta workflows/blueprints e incluye instrucciones de importación.

---

## 5. Criterios de evaluación

Tu solución se evaluará con la siguiente rúbrica (100 puntos):

| Criterio | Peso | Qué evaluamos |
|----------|------|----------------|
| **Arquitectura y diseño técnico** | 15% | Componentes, patrones, escalabilidad, justificación de decisiones |
| **Calidad del bot** | 35% | Precisión, consultas complejas, experiencia de usuario |
| **Calidad de insights** | 30% | Relevancia, profundidad, accionabilidad de insights automáticos |
| **Código y documentación** | 5% | Limpieza, reproducibilidad, claridad |
| **Presentación y comunicación** | 20% | Claridad en la demo y explicación técnica |

**Lo que buscamos en un candidato excepcional**

- **Pensamiento estratégico:** no solo resolver el problema, sino proponer mejoras y extensiones
- **Balance técnico–negocio:** el objetivo es valor, no solo código elegante
- **Creatividad** ante los retos del caso
- **Atención al detalle:** casos límite, validaciones, UX

---

## 6. Formato de entrega

### Repositorio

Sube tu solución a un repositorio Git (GitHub, GitLab, etc.) y comparte el enlace. Debe ser **público** o facilitar acceso.

### Presentación (30 minutos)

Estructura sugerida:

1. **Contexto y enfoque** (3 min): cómo interpretaste el problema
2. **Demo del bot** (10 min): al menos 5 preguntas de distinta complejidad
3. **Insights automáticos** (5 min): reporte generado y hallazgos
4. **Decisiones técnicas** (5 min): arquitectura, LLM, trade-offs
5. **Limitaciones y próximos pasos** (2 min): qué mejorarías con más tiempo
6. **Q&A** (10 min)

**Importante:** **demo en vivo**, no solo video grabado. El sistema debe funcionar en tiempo real.

---

## 7. Preguntas frecuentes

**¿Puedo usar librerías de terceros para gráficos o análisis?**  
Sí (plotly, matplotlib, seaborn, pandas, numpy, scikit-learn, etc.).

**¿Qué pasa si no completo todos los bonus?**  
Los bonus no son obligatorios. Mejor un caso sólido sin bonus que uno con bonus y baja calidad.

**¿Puedo hacer preguntas durante el caso?**  
Para dudas **conceptuales** sobre métricas de negocio: **daniel.chain@rappi.com**.

**¿Necesito deployment en la nube?**  
No es obligatorio; localhost basta. Deployment (Streamlit Cloud, Render, Railway, etc.) es un plus.

**¿Qué tan sofisticado debe ser el sistema de insights?**  
Prioriza **relevancia sobre complejidad.** Cinco insights bien fundamentados valen más que veinte superficiales.

---

## 8. Datos de contacto y timeline

| | |
|--|--|
| **Envío de materiales** | CSVs junto con este brief |
| **Fecha límite de entrega** | 2025-10-13 |
| **Fecha de presentación** | A coordinar después de entrega |
| **Contacto para dudas** | daniel.chain@rappi.com |

---

## 9. Consejos finales

- **Empieza simple:** un bot básico que funcione bien vale más que uno ambicioso que falle
- **Documenta decisiones:** por qué elegiste framework X o modelo Y
- **Piensa en el usuario final:** ¿un operational manager lo usaría de verdad?
- **Gestiona el tiempo:** prioriza requisitos obligatorios

**¡Mucha suerte!** Estamos entusiasmados por ver tu solución.

---

*Nota: los datos han sido anonimizados y aleatorizados; no representan un país ni período específico.*
