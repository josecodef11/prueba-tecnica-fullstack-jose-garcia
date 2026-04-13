# Propuesta: App Flutter para Eventos



Una aplicación móvil en Flutter que consume la API de eventos del backend FastAPI. Permite ver una lista de eventos, filtrar por fechas, paginar resultados y ver detalles de cada evento.

Arquitectura

Usamos una arquitectura **feature-first** (por módulos) combinada con **Clean Architecture** ligera. Esto significa organizar el código por funcionalidades (como "eventos") en lugar de por tipos de archivos (models, services, etc.).

Tecnologías Principales

- **Riverpod**: Para manejar el estado de la app (loading, datos, errores)
- **Dio**: Para hacer llamadas HTTP a la API
- **Repository Pattern**: Para separar la lógica de acceso a datos

Estructura de Carpetas 

```
lib/
├── app/
│   ├── app.dart
│   ├── router.dart
│   ├── env.dart
│   └── providers.dart
├── core/
│   ├── network/
│   │   ├── dio_client.dart
│   │   ├── api_result.dart
│   │   └── interceptors/
│   ├── errors/
│   │   ├── app_exception.dart
│   │   └── failure.dart
│   ├── utils/
│   └── widgets/
├── features/
│   └── events/
│       ├── data/
│       │   ├── datasources/
│       │   │   └── events_remote_datasource.dart
│       │   ├── dtos/
│       │   │   ├── event_list_item_dto.dart
│       │   │   ├── event_detail_dto.dart
│       │   │   └── paginated_events_dto.dart
│       │   ├── mappers/
│       │   └── repositories/
│       │       └── events_repository.dart
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── event_item.dart
│       │   │   ├── event_detail.dart
│       │   │   └── paginated_events.dart
│       │   ├── repositories/
│       │   │   └── events_repository.dart
│       │   └── usecases/
│       │       ├── get_events.dart
│       │       └── get_event_detail.dart
│       └── presentation/
│           ├── providers/
│           │   ├── events_list_provider.dart
│           │   ├── event_detail_provider.dart
│           │   └── events_filters_provider.dart
│           ├── screens/
│           │   ├── events_page.dart
│           │   └── event_detail_page.dart
│           └── widgets/
│              
└── main.dart
```

Cómo Funciona el Flujo de Datos

1. **UI** (pantallas) observa el estado usando Riverpod
2. **Providers** (Riverpod) gestionan estado y llaman a repositorios
3. **Repositorios** coordinan la lógica de negocio
4. **DataSources** hacen las llamadas HTTP con Dio
5. **API** (backend) devuelve datos JSON

Ventajas de Esta Arquitectura

- **Escalable**: Fácil agregar nuevas funcionalidades sin mezclar código
- **Mantenible**: Cambios en la API afectan solo una capa
- **Testeable**: Cada parte se puede probar por separado
- **Reutilizable**: Componentes compartidos entre pantallas

Implementación por Fases

Fase 1: Base (Core)
- Configurar Dio para llamadas HTTP
- Crear widgets básicos (loading, error)

Fase 2: Datos (Data Layer)
- Definir modelos para respuestas de API
- Crear llamadas a `/events` y `/events/{id}`

Fase 3: Lógica (Domain)
- Definir modelos de negocio
- Crear interfaces para repositorios

Fase 4: UI (Presentation)
- Pantalla de lista con filtros y paginación
- Pantalla de detalle de evento
- Providers para estado

Fase 5: Integración
- Conectar todo y probar


