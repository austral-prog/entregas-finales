# 📋 Estado de Entregas Finales — DCP / Proyecto de Software

Sitio web estático para el seguimiento público del estado de entregas finales de los alumnos de Diseño y Construcción de Programas (Facultad de Ingeniería, Universidad Austral).

## Requisitos de Entrega
Cada alumno desarrollador debe entregar:
1. **PDF de Tareas Realizadas**: Documento con el listado detallado de tareas cumplidas a lo largo del cuatrimestre.
2. **Video Demo del Proyecto**: Demostración grabada en video del proyecto funcional.
3. **Video del Bug Encontrado**: Demostración grabada de un bug o caso de prueba detectado.

*(Opcional: Planilla Excel de evaluación de líderes de 5to año).*

## Funcionalidades del Sitio
- 📊 **Métricas en tiempo real**: Alumnos al día (3/3), parciales y pendientes.
- 👥 **Vista por Alumno**: Tabla interactiva con búsqueda por nombre, filtros por entrega faltante y enlaces a los archivos/videos entregados.
- 🏷️ **Vista por Grupo**: Tarjetas de los 16 proyectos con progreso grupal y botón para copiar aviso formateado para Discord/Slack.
- 📥 **Exportación**: Descarga directa a archivo CSV para abrir en Excel o Google Sheets.
- 💬 **Generador de Mensajes**: Mensajes listos para enviar a alumnos individuales o canales generales.

## Actualización de Datos
El sitio se compila ejecutando:
```bash
python build.py
```
Los datos provienen de `interviews-log/backend/data/deliverables.json`.
