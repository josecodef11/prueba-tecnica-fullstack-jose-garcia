<?php
$API_BASE = getenv('API_BASE_URL') ?: 'http://localhost:8000';
?>
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Módulo de Eventos</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

  <style>
    body {
      background: linear-gradient(180deg, #f7f8fb 0%, #eef2f7 100%);
      min-height: 100vh;
    }

    .page-shell {
      max-width: 1200px;
    }

    .event-row:hover {
      background: rgba(13, 110, 253, 0.04);
    }

    .table thead th {
      white-space: nowrap;
    }

    .table td {
      vertical-align: middle;
    }
  </style>
</head>
<body>

<nav class="navbar navbar-dark bg-dark shadow-sm">
  <div class="container page-shell">
    <span class="navbar-brand mb-0 h1">
      <i class="bi bi-calendar-event me-2"></i>Eventos
    </span>
    <span class="text-white-50 small" id="total-label">Cargando...</span>
  </div>
</nav>

<main class="container page-shell py-4">
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <label for="filter-from" class="form-label">Desde</label>
          <input type="date" id="filter-from" class="form-control">
        </div>
        <div class="col-md-4">
          <label for="filter-to" class="form-label">Hasta</label>
          <input type="date" id="filter-to" class="form-control">
        </div>
        <div class="col-md-4 d-flex gap-2">
          <button type="button" id="btn-filter" class="btn btn-primary flex-fill">
            <i class="bi bi-search me-1"></i>Filtrar
          </button>
          <button type="button" id="btn-clear" class="btn btn-outline-secondary">
            Limpiar
          </button>
        </div>
      </div>
      <div class="small text-muted mt-2" id="date-range-help"></div>
    </div>
  </div>

  <div id="loading" class="text-center py-5 d-none">
    <div class="spinner-border text-primary" role="status"></div>
    <p class="text-muted mt-3 mb-0">Cargando eventos...</p>
  </div>

  <div id="error-box" class="alert alert-danger d-none"></div>

  <div class="card shadow-sm border-0">
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th>Fecha</th>
              <th>Título</th>
              <th>Organizador</th>
              <th>Dirección</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="events-body">
            <tr>
              <td colspan="5" class="text-center py-5 text-muted">Cargando eventos...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-2">
    <button id="btn-prev" class="btn btn-outline-primary">Anterior</button>
    <span id="page-info" class="text-muted"></span>
    <button id="btn-next" class="btn btn-outline-primary">Siguiente</button>
  </div>
</main>

<div class="modal fade" id="eventModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modal-title">Detalle del evento</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
      </div>
      <div class="modal-body">
        <div id="modal-loading" class="text-center py-4 d-none">
          <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div id="modal-error" class="alert alert-danger d-none"></div>

        <div id="modal-content" class="d-none">
          <div class="row g-3">
            <div class="col-md-6">
              <div class="text-muted small">Fecha</div>
              <div id="modal-date" class="fw-semibold"></div>
            </div>
            <div class="col-md-6">
              <div class="text-muted small">Organizador</div>
              <div id="modal-organizer"></div>
            </div>
            <div class="col-12">
              <div class="text-muted small">Descripción</div>
              <div id="modal-description"></div>
            </div>
            <div class="col-12">
              <div class="text-muted small">Dirección</div>
              <div id="modal-address"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
  const API_BASE = "<?= rtrim($API_BASE, '/') ?>";
  const PAGE_SIZE = 10;

  let currentPage = 1;
  let totalPages = 1;
  let dateRange = { min: '', max: '' };

  const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));

  function escapeHtml(value) {
    return $('<div>').text(value ?? '').html();
  }

  function formatDate(value) {
    if (!value) return 'Sin fecha';
    return new Date(value).toLocaleString('es-CO', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  }

  function setLoading(show) {
    $('#loading').toggleClass('d-none', !show);
  }

  function setError(message) {
    $('#error-box').text(message || '').toggleClass('d-none', !message);
  }

  function setDateRange(range) {
    dateRange = range || { min: '', max: '' };
    $('#filter-from').attr('min', dateRange.min || '');
    $('#filter-from').attr('max', dateRange.max || '');
    $('#filter-to').attr('min', dateRange.min || '');
    $('#filter-to').attr('max', dateRange.max || '');

    if (dateRange.min && dateRange.max) {
      $('#date-range-help').text(`Rango disponible: ${dateRange.min} a ${dateRange.max}`);
    } else {
      $('#date-range-help').text('');
    }
  }

  function normalizeDateInputs() {
    const from = $('#filter-from').val();
    const to = $('#filter-to').val();

    if (from && dateRange.min && from < dateRange.min) {
      $('#filter-from').val(dateRange.min);
    }

    if (to && dateRange.max && to > dateRange.max) {
      $('#filter-to').val(dateRange.max);
    }
  }

  function renderEmpty(message) {
    $('#events-body').html(
      `<tr><td colspan="5" class="text-center py-5 text-muted">${escapeHtml(message)}</td></tr>`
    );
  }

  function renderEvents(items) {
    if (!items.length) {
      renderEmpty('No se encontraron eventos.');
      return;
    }

    const rows = items.map(function(event) {
      return `
        <tr class="event-row">
          <td>${escapeHtml(formatDate(event.date))}</td>
          <td>
            <strong>${escapeHtml(event.title)}</strong>
          </td>
          <td>${escapeHtml(event.organizer || 'Sin organizador')}</td>
          <td>${escapeHtml(event.address || 'Sin ubicación')}</td>
          <td class="text-end">
            <button type="button" class="btn btn-sm btn-outline-primary js-detail" data-id="${event.id}" data-title="${escapeHtml(event.title)}">
              Ver detalle
            </button>
          </td>
        </tr>
      `;
    }).join('');

    $('#events-body').html(rows);
  }

  function loadDateRange() {
    return $.ajax({
      url: `${API_BASE}/events/date-range`,
      method: 'GET',
      dataType: 'json'
    }).done(function(data) {
      setDateRange({
        min: data.min_date ? data.min_date.slice(0, 10) : '',
        max: data.max_date ? data.max_date.slice(0, 10) : ''
      });
    });
  }

  function loadEvents(page) {
    currentPage = page || 1;
    setLoading(true);
    setError('');

    const params = {
      page: currentPage,
      size: PAGE_SIZE
    };

    const fromValue = $('#filter-from').val();
    const toValue = $('#filter-to').val();

    if (fromValue) params.from = fromValue;
    if (toValue) params.to = toValue;

    $.ajax({
      url: `${API_BASE}/events`,
      method: 'GET',
      data: params,
      dataType: 'json'
    })
      .done(function(data) {
        totalPages = data.pages || 1;

        $('#total-label').text(`${data.total || 0} evento${(data.total || 0) === 1 ? '' : 's'}`);
        $('#page-info').text(`Página ${data.page || 1} de ${totalPages}`);
        $('#btn-prev').prop('disabled', (data.page || 1) <= 1);
        $('#btn-next').prop('disabled', (data.page || 1) >= totalPages);

        renderEvents(data.results || []);
      })
      .fail(function() {
        setError('No se pudo conectar con el backend.');
        renderEmpty('No se pudo cargar la lista.');
      })
      .always(function() {
        setLoading(false);
      });
  }

  function loadEventDetail(id, title) {
    $('#modal-title').text(title);
    $('#modal-loading').removeClass('d-none');
    $('#modal-error').addClass('d-none');
    $('#modal-content').addClass('d-none');
    eventModal.show();

    $.ajax({
      url: `${API_BASE}/events/${id}`,
      method: 'GET',
      dataType: 'json'
    })
      .done(function(event) {
        $('#modal-date').text(formatDate(event.date));
        $('#modal-organizer').text(event.organizer || 'No especificado');
        $('#modal-description').text(event.description || 'Sin descripción');
        $('#modal-address').text((event.location && event.location.address) || event.address || 'Sin dirección');
        $('#modal-content').removeClass('d-none');
      })
      .fail(function() {
        $('#modal-error').text('No se pudo cargar el detalle del evento.').removeClass('d-none');
      })
      .always(function() {
        $('#modal-loading').addClass('d-none');
      });
  }

  $(function() {
    $('#btn-filter').on('click', function() {
      normalizeDateInputs();
      loadEvents(1);
    });

    $('#btn-clear').on('click', function() {
      $('#filter-from').val('');
      $('#filter-to').val('');
      loadEvents(1);
    });

    $('#btn-prev').on('click', function() {
      if (currentPage > 1) loadEvents(currentPage - 1);
    });

    $('#btn-next').on('click', function() {
      if (currentPage < totalPages) loadEvents(currentPage + 1);
    });

    $('#events-body').on('click', '.js-detail', function() {
      loadEventDetail($(this).data('id'), $(this).data('title'));
    });

    loadDateRange()
      .always(function() {
        loadEvents(1);
      });
  });
</script>
</body>
</html>
