# Fase 3 — Empaquetado y demo (completada)

**Plan:** `plan/plan_operaciones.md` § Fase 3

---

## Qué cubre esta fase

| Entregable | Dónde quedó |
|------------|-------------|
| README con setup, env, comandos | `README.md` (raíz) |
| Coste estimado API | Sección en `README.md` (orden de magnitud; verificar precios oficiales) |
| Lista de pruebas pre-demo | `docs/demo_checklist_operaciones.md` |
| Guion alineado al brief | Mismo archivo + resumen abajo |

---

## Resumen del guion (30 min)

1. **Contexto** — Problema: datos fragmentados y análisis manual; solución: bot NL + insights automáticos.
2. **Demo bot** — ≥5 preguntas de tipos distintos (ver checklist).
3. **Insights** — Abrir HTML/PDF generado; comentar 2–3 hallazgos y recomendaciones.
4. **Técnica** — OpenAI function calling + `ToolExecutor` (pandas); informe sin LLM; `gpt-4o-mini`.
5. **Limitaciones** — Datos sintéticos; posibles % extremos; sin deploy obligatorio; gráficos en bot no implementados (bonus).

---

## Comandos rápidos

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run operaciones/app.py
python -m operaciones.generate_report
```

Checklist detallado: **`docs/demo_checklist_operaciones.md`**.
