# Caso técnico: sistema de Competitive Intelligence para Rappi

**Rol:** AI Engineer  

**Tiempo para la entrega:** 2 días calendario  

**Formato de presentación:** 30 minutos (20 min presentación + 10 min Q&A)

---

## 1. Contexto del problema

Rappi compite en un mercado altamente dinámico con jugadores como Uber Eats, DiDi Food, PedidosYa, iFood, Cornershop y otros operadores locales. Los precios, tiempos de entrega y fees cambian constantemente según:

- Promociones y descuentos dinámicos
- Disponibilidad de repartidores
- Demanda en tiempo real
- Estrategias competitivas por zona

Actualmente, **no tenemos visibilidad sistemática** de cómo nos comparamos con la competencia en estas variables críticas. Los equipos de Pricing, Operations y Strategy toman decisiones sin datos actualizados sobre:

- ¿Somos más caros o baratos que la competencia en cada zona?
- ¿Nuestros tiempos de entrega son competitivos?
- ¿Cómo se comparan nuestros service fees?
- ¿Qué promociones está corriendo la competencia?

**Tu misión** es construir un sistema automatizado que recolecte datos de la competencia y genere insights accionables para la toma de decisiones estratégicas.

---

## 2. Entregables requeridos

### 2.1 Sistema de scraping competitivo (70% del peso)

Desarrolla un sistema que recolecte datos de al menos **2 competidores** (además de Rappi) en **20–50 direcciones representativas**.

**Requisitos mínimos**

- **Recolección de datos** de las siguientes plataformas en **México:**
  - Rappi (para baseline propio)
  - Uber Eats
  - DiDi Food
- **Métricas a recolectar** (mínimo 3 de las siguientes):
  - **Precio del producto:** precio de 3–5 ítems comparables (ej.: Big Mac, combo McDonald’s, Coca-Cola 500 ml)
  - **Delivery fee:** costo de envío antes de descuentos
  - **Service fee:** comisión de la plataforma
  - **Tiempo estimado de entrega:** promedio o rango mostrado al usuario
  - **Descuentos activos:** promociones, cupones, ofertas visibles
  - **Disponibilidad:** restaurantes/tiendas disponibles vs cerrados
  - **Precio final total:** precio que realmente paga el usuario
- **Cobertura geográfica:**
  - Selecciona **20–50 direcciones representativas** que cubran distintos tipos de zonas.
  - Documenta con claridad las direcciones elegidas y la justificación.
- **Automatización:**
  - El sistema debe poder ejecutarse con un comando o script.
  - **Output:** CSV o JSON con los datos recolectados.

**Bonus (no obligatorio)**

- Scraping de múltiples verticales (restaurantes + retail + farmacia)
- Comparación del mismo restaurante en distintas plataformas
- Capturas automáticas de pantalla como evidencia

### 2.2 Informe de insights competitivos (30% del peso)

Genera un informe analítico con hallazgos accionables basados en los datos recolectados.

**Requisitos mínimos**

- **Análisis comparativo estructurado:**
  - **Posicionamiento de precios:** ¿dónde está Rappi vs competencia? (más caro, más barato, similar)
  - **Ventaja/desventaja operacional:** tiempos de entrega comparados
  - **Estructura de fees:** cómo se comparan delivery fees y service fees
  - **Estrategia promocional:** qué tipo de descuentos usa cada competidor
  - **Variabilidad geográfica:** ¿la competitividad varía por zona?
- **Top 5 insights accionables:** cada insight debe incluir:
  - **Finding:** ¿qué descubriste?
  - **Impacto:** ¿por qué es importante?
  - **Recomendación:** ¿qué debería hacer Rappi?

**Ejemplo**

- **Finding:** Uber Eats tiene delivery fees ~40% más bajos en zonas periféricas.
- **Impacto:** estamos perdiendo competitividad en zonas de expansión.
- **Recomendación:** considerar subsidiar delivery fee en zonas prioritarias X, Y, Z.

- **Visualizaciones claras:**
  - Al menos 3 gráficos que soporten tus insights
  - Comparaciones directas (barras, tablas, heatmaps)
- **Formato:**
  - Documento ejecutivo (PDF, PowerPoint, Notion o dashboard interactivo)
  - Debe ser accionable para equipos de Strategy y Pricing

**Bonus (no obligatorio)**

- Dashboard interactivo (Streamlit, Tableau, Power BI)
- Análisis de tendencias temporales (si hiciste múltiples scrapes)

---

## 3. Scope y limitaciones

Dada la complejidad del scraping y el tiempo limitado, **define un scope realista.**

**Productos de referencia** — para comparar precios de forma consistente, usa productos estandarizados.

**Fast food**

- Big Mac o Whopper
- Combo mediano (hamburguesa + papas + bebida)
- Nuggets (6 o 10 piezas)

**Retail**

- Coca-Cola 500 ml
- Agua embotellada 1 L
- Paquete de pañales (marca reconocida)

---

## 4. Requisitos técnicos

### Stack tecnológico

**Libertad total de herramientas**

- **Scraping:** Selenium, Playwright, Puppeteer, BeautifulSoup, Scrapy, APIs no oficiales
- **Proxies / anti-detección:** si es necesario (Bright Data, ScraperAPI, proxies rotativos)
- **Automatización:** cron jobs, GitHub Actions, Airflow, Make, n8n
- **Análisis:** Python (pandas, matplotlib), R, JavaScript, notebooks
- **Dashboards:** Streamlit, Plotly Dash, Tableau, Power BI, Metabase

**Consideraciones**

- Si usas servicios pagos (proxies, APIs), documenta costos.
- El scraping debe ser **reproducible** por el equipo evaluador.

### Código y reproducibilidad

- Incluye un **README** con:
  - Instrucciones de setup (dependencias, API keys, configuración)
  - Cómo ejecutar el scraper
  - Cómo generar el informe
  - Limitaciones conocidas
- **Output estructurado:**
  - CSV/JSON con los datos raw recolectados
  - Informe final (PDF, HTML o enlace a dashboard)
- **Ética y legalidad:**
  - Respeta `robots.txt` cuando sea posible
  - No sobrecargues los servidores (rate limiting razonable)
  - Usa user-agents apropiados
  - Documenta consideraciones éticas de tu enfoque

### Buenas prácticas (valoradas, no obligatorias)

- Rate limiting y delays para no saturar servidores
- Logging de errores y scraping exitoso
- Lógica de reintentos ante fallos temporales
- Código modular y reutilizable
- Tests básicos (si aplica)

---

## 5. Criterios de evaluación

Tu solución se evaluará con la siguiente rúbrica (100 puntos):

| Criterio | Peso | Qué evaluamos |
|----------|------|----------------|
| **Calidad del scraping** | 50% | Completitud de datos, manejo de errores, robustez del sistema |
| **Calidad de insights** | 15% | Relevancia, profundidad, accionabilidad de hallazgos |
| **Diseño técnico** | 10% | Arquitectura, elección de herramientas, escalabilidad |
| **Documentación** | 5% | Claridad de instrucciones, reproducibilidad |
| **Presentación** | 20% | Claridad en la demo y comunicación de findings |

**Lo que buscamos en un candidato excepcional**

- **Pragmatismo:** scope bien definido vs querer scrapear todo el universo
- **Pensamiento estratégico:** insights que muevan la aguja del negocio
- **Resiliencia técnica:** manejo de casos límite (productos no disponibles, sitios bloqueados, etc.)
- **Business acumen:** entender qué métricas importan y por qué

---

## 6. Formato de entrega

### Repositorio

Sube tu solución a un repositorio Git (GitHub, GitLab, etc.) y comparte el enlace. Debe ser **público** o facilitar acceso.

### Presentación (30 minutos)

Estructura sugerida:

1. **Approach y scope** (3 min): qué decidiste scrapear y por qué
2. **Demo del sistema** (7 min): ejecuta el scraper en vivo (o grabación si hay riesgo de bloqueos)
3. **Datos recolectados** (3 min): panorama de la data obtenida
4. **Top 5 insights** (10 min): hallazgos clave con visualizaciones
5. **Decisiones técnicas** (4 min): desafíos y soluciones
6. **Limitaciones y próximos pasos** (3 min): qué mejorarías con más tiempo
7. **Q&A** (10 min)

**Nota:** si el scraping en vivo es arriesgado, lleva datos pre-scrapeados como respaldo.

---

## 7. Preguntas frecuentes

**¿Puedo usar APIs no oficiales o reverse-engineered?**  
Sí, si es más eficiente que scrapear HTML. Documenta tu enfoque.

**¿Qué pasa si me bloquean durante el scraping?**  
Forma parte del reto. Usa proxies, rate limiting, headers y documenta limitaciones. No se penaliza el bloqueo si el diseño es sólido.

**¿Debo scrapear en tiempo real en la presentación?**  
Recomendamos datos pre-scrapeados como respaldo. Live demo es bienvenida si tienes plan B.

**¿Necesito scrapear todos los competidores?**  
No. 2 competidores + Rappi es suficiente. Prioriza calidad sobre cantidad.

**¿Puedo usar servicios pagos (Bright Data, ScraperAPI)?**  
Sí; documenta costos. Se valoran soluciones cost-effective.

**¿Qué pasa si algunos datos no están disponibles?**  
Documenta qué obtuviste y qué no, y los bloqueadores en la presentación.

**¿Es legal hacer scraping?**  
Los datos públicos suelen ser analizables con fines competitivos, pero debes respetar términos de servicio y no sobrecargar servidores. Revisa implicaciones en tu jurisdicción.

---

## 8. Datos de contacto y timeline

| | |
|--|--|
| **Envío de materiales** | Recibirás este brief |
| **Fecha límite de entrega** | 13/10/2025 |
| **Fecha de presentación** | A coordinar después de entrega |
| **Contacto para dudas** | daniel.chain@rappi.com |

---

## 9. Consejos finales

- Define un **scope alcanzable:** mejor pocas direcciones bien scrapeadas que muchas a medias
- **Prioriza robustez:** el scraping falla; diseña con eso en mente
- **Piensa como strategist:** los insights pesan más que el volumen de datos
- **Documenta blockers:** si algo no funciona, explica por qué y qué intentaste
- **Ten un plan B:** los sitios pueden caerse el día de la demo
- **Empieza simple:** un producto en 3 direcciones bien comparadas vale más que 10 productos superficiales

**Consideración ética:** este ejercicio es para reclutamiento. En producción, consulta con Legal antes de scraping sistemático.

**¡Mucha suerte!** Queremos ver tu capacidad de resolver problemas reales con restricciones realistas.

---

*Nota: este caso evalúa tu capacidad de extraer inteligencia competitiva de fuentes públicas. El scraping debe realizarse de manera ética y responsable.*
