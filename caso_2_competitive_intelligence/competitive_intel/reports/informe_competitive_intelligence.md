# Informe — Competitive Intelligence (México)

_Fuente CSV: `scrape_latest.csv`. Filas: 180._

## Comparativo rápido

- **Ticket medio más bajo:** `rappi` (~129.0 MXN vs `uber_eats` ~308.3 MXN).
- **Delivery fee más bajo en promedio:** `rappi`.
- **Menor ETA medio:** `uber_eats` (~10 min).
- **Ciudad con mayor dispersión entre plataformas (ticket):** `Ciudad de México`.
- **Tasa filas con promoción visible (no 'Ninguna'):** `didi_food` 100%, `rappi` 100%, `uber_eats` 100%

## Visualizaciones

![Total por plataforma](figures/fig1_total_by_platform.png)

![Fees](figures/fig2_fees_by_platform.png)

![ETA](figures/fig3_eta_by_platform.png)

## Top 5 insights accionables

1. **Finding:** En este dataset, `rappi` muestra ticket medio más bajo que `uber_eats`.  
   **Impacto:** Percepción de precio y conversión en carrito pueden verse afectadas en zonas sensibles al precio.  
   **Recomendación:** Revisar bundle/promos en ciudades donde la brecha vs `rappi` sea mayor al percentil 75.

2. **Finding:** `rappi` concentra delivery fees medios más bajos.  
   **Impacto:** Competencia en costo de envío en zonas periféricas.  
   **Recomendación:** Simular subsidio parcial de envío en `zone_type=periphery` priorizado.

3. **Finding:** `uber_eats` lidera ETA medio en datos sintéticos/demo.  
   **Impacto:** Expectativa de tiempo en UX y retención.  
   **Recomendación:** Mapear zonas donde ETA Rappi supere competencia en scrape real y ajustar SLAs operativos.

4. **Finding:** Mezcla de promos visibles difiere por plataforma en el CSV.  
   **Impacto:** Guerra promocional en adquisición.  
   **Recomendación:** Tablero semanal de tipo de promo por zona y vertical (extender scrape).

5. **Finding:** Alta variabilidad inter-plataforma en `Ciudad de México`.  
   **Impacto:** Pricing inconsistente percibido por usuario.  
   **Recomendación:** Deep-dive de fees + restaurante ancla (misma cadena cross-app) en esa ciudad.

---
_Datos demo: reemplazar con scrape real para decisiones de producción._
