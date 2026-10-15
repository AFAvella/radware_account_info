# Radware Account Health Analyzer

Aplicación web interna de solo lectura, construida con Streamlit, para consultar información de Application Protection en Radware Cloud y revisar adopción de protecciones por aplicación.

## Qué hace actualmente

- `app.py` presenta la conexión y organiza los paneles.
- `radware_client.py` consulta la API de Radware Cloud con la API Key y el Context ID ingresados por el usuario.
- `modules/application_adoption.py` consulta aplicaciones, detalles y políticas, normaliza estados y presenta una matriz con exportación CSV.
- `modules/entitlement_profiles.py` permite ingresar manualmente la capacidad de aplicaciones, las funcionalidades licenciadas y cuáles deben estar en modo Blocking.
- `modules/waf_progress.py` calcula el avance de las aplicaciones incluidas en el análisis.
- `modules/security_recommendations.py` genera recomendaciones a partir de las funcionalidades licenciadas seleccionadas.

La selección de capacidades por cliente es manual y se mantiene solamente en la sesión actual de Streamlit. No se consulta ni se persiste el contrato/licencia. Los perfiles comerciales predefinidos deben agregarse cuando se confirme su matriz de funcionalidades.

## Medición del avance WAF

1. Ingrese la capacidad licenciada de aplicaciones.
2. Seleccione las funcionalidades incluidas en la licencia.
3. Marque cuáles de esas funcionalidades deben estar en Blocking. Las demás se evalúan como activas/configuradas; Report Only y Passive cuentan como activas para esas funcionalidades.
4. En el panel, seleccione las aplicaciones que se incluirán en el análisis. Por defecto se incluyen todas las recibidas de la API.

La fórmula es:

`avance (%) = requisitos cumplidos / (aplicaciones seleccionadas × funcionalidades licenciadas) × 100`

Un requisito de Blocking solo se cumple cuando el estado observado es `BLOCK`, `BLOCK_AND_REPORT` o `ENABLE_AND_REPORT`. Para las otras funcionalidades, estados activos/configurados y Report Only/Passive cumplen el objetivo. Estados deshabilitados o no configurados son faltantes. Estados ausentes, `N/A` o no reconocidos son **no confirmados**: permanecen en el denominador, no se cuentan como implementados y se muestran por separado.

Si no se marca ninguna funcionalidad como requisito de Blocking, el porcentaje medirá únicamente activación/configuración; la interfaz lo indica para evitar interpretar ese valor como cobertura efectiva en modo bloqueo.

El uso de capacidad se muestra independientemente como aplicaciones seleccionadas/capacidad licenciada. Por ejemplo, 3 aplicaciones seleccionadas completamente implementadas de una capacidad de 10 pueden mostrar 100% de avance y 30% de capacidad utilizada; las plazas licenciadas sin aplicación no reducen el avance técnico.

Un porcentaje de 0% o `N/A` debe interpretarse junto con las métricas de faltantes y estados no confirmados. La precisión depende de los estados que la API proporcione y de la selección manual de funcionalidades y objetivos. La herramienta todavía no valida automáticamente aplicabilidad de cada funcionalidad por aplicación.

## Ejecución

Instale las dependencias listadas en `requirements.txt` y ejecute:

```powershell
streamlit run app.py
```