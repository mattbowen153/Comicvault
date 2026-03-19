<script>
  let comics = JSON.parse(localStorage.getItem('comics')) || [];

  function startScanner() {
    alert("Scanner started! (Test mode - camera permission will be requested)");
    // Real scanner code can go here later
  }

  function renderCollection() {
    const list = document.getElementById('comic-list');
    list.innerHTML = '';
    comics.forEach(c => {
      const div = document.createElement('div');
      div.innerHTML = `<div style="background:#16161f;padding:1rem;margin:1rem;border-radius:12px;">
        <h3>${c.title || 'Unknown'} #${c.issue || '?'}</h3>
        <p>Grade: ${c.grade || '?'}</p>
        <p>Value: $${c.value || 0}</p>
      </div>`;
      list.appendChild(div);
    });
  }

  renderCollection();
</script>
