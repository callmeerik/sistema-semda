let confirmCallback = null;

function openConfirmModal({ title, message, onConfirm }) {
  document.getElementById('confirmTitle').textContent = title;
  document.getElementById('confirmMessage').textContent = message;

  confirmCallback = onConfirm;

  const modal = document.getElementById('confirmModal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function closeConfirmModal() {
  const modal = document.getElementById('confirmModal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  confirmCallback = null;
}

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('confirmActionBtn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    if (confirmCallback) confirmCallback();
    closeConfirmModal();
  });
});
