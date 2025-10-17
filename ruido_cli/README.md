# Consultas a servicios de ruido (SIATA) – GUI

Aplicación con interfaz gráfica para consultar estaciones y descargar datos en CSV sin tocar código. Usa `config.yaml` para endpoints y `.env` para el token.

## Requisitos

- Windows con Python 3.10+ (la app crea un entorno virtual automáticamente)

## Primeros pasos (GUI)

1) Abre `run_ruido_gui.bat` (doble clic). Si es la primera vez, instalará dependencias.

2) En la ventana:
- Token (x-token): pega tu token o déjalo cargado desde `.env` (`AMVA_TOKEN`).
- Inicio / Fin: formato `YYYY-MM-DD hh:mm:ss`. Rango máximo validado: 62 días.
- Estación: se llena tras pulsar “Actualizar estaciones”.

3) Botones principales:
- Actualizar estaciones: descarga catálogo y guarda `data/stations.csv`.
- Stations → CSV: vuelve a exportar el catálogo.
- Todas estaciones → CSV: baja datos para el rango y guarda `data/all_stations_noise_data.csv` (consulta en tramos para evitar timeouts).
- Una estación → CSV: selecciona la estación y guarda `data/station_noise_data.csv`.

Notas:
- Si el servicio demora, se aplican reintentos automáticos y partición del rango en bloques de 14 días.
- Los CSV se guardan en `ruido_cli/data`.

## Configuración

- `.env`
```
AMVA_TOKEN=tu_token_aqui
```
- `config.yaml`: contiene `base_url`, autenticación `x-token` y rutas. No es necesario editarlo para el uso normal.

## (Opcional) Uso por línea de comando

- Puedes usar `run_ruido_cli.bat` desde PowerShell/CMD si prefieres CLI:
```
./run_ruido_cli.bat listar
./run_ruido_cli.bat ejecutar stations --json
./run_ruido_cli.bat ejecutar all_stations_noise_data --param start_date="2025-08-01 00:00:00" --param end_date="2025-09-30 23:59:59"
```

