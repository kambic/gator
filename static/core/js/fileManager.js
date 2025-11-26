Alpine.data('fileExploreraa', () => ({
  path: '',
  files: [],
  breadcrumbs: [],
  loading: false,
  error: '',

  loadFiles() {
    this.loading = true;
    this.error = '';

    const pathParts = this.path.split('/').filter(Boolean);
    this.breadcrumbs = pathParts;

    // NOTE: The URL 'core:file_api' MUST be resolvable when Django renders the template
    // Since we are in an external JS file, we cannot use {% url %}.
    // A better solution would be to define this endpoint globally in the HTML.
    // For now, I'll use a placeholder URL and rely on you to define it dynamically
    // in the HTML if needed, but I'll stick to the original plan of making it a dynamic part of the code.
    // Because the original code used {% url 'core:file_api' %},
    // I will assume the base URL is globally available as window.FILE_API_URL
    // and adjust the fetch call accordingly.

    // Since I cannot access Django variables here, I will modify the HTML to pass the URL.
    // I will use a generic placeholder here and rely on the HTML to define the API endpoint globally.

    const apiUrl = window.FILE_API_URL || '/api/files/';

    fetch(`${apiUrl}?path=${encodeURIComponent(this.path)}`)
      .then((r) => {
        if (!r.ok) {
          return r.json().then((err) => {
            throw new Error(err.detail || 'Failed to load files.');
          });
        }
        return r.json();
      })
      .then((data) => {
        this.files = data;
      })
      .catch((e) => {
        console.error('File Explorer Error:', e);
        this.error = e.message || 'An unknown error occurred while fetching files.';
        this.files = [];
      })
      .finally(() => {
        this.loading = false;
      });
  },

  openDir(p) {
    this.path = p;
    this.loadFiles();
  },

  goTo(index) {
    if (index === -1) {
      // Root navigation
      this.path = '';
    } else {
      this.path = this.breadcrumbs.slice(0, index + 1).join('/');
    }
    this.loadFiles();
  },

  deleteFile(path) {
    // Using a custom modal/toast is better than 'confirm' for production UI
    if (!window.confirm(`Are you sure you want to delete "${path.split('/').pop()}"?`)) return;
    this.loading = true;
    this.error = '';

    const deleteUrl = window.FILE_API_URL
      ? `${window.FILE_API_URL}?path=${encodeURIComponent(path)}`
      : `/api/files/?path=${encodeURIComponent(path)}`;

    fetch(deleteUrl, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) {
          return r.json().then((err) => {
            throw new Error(err.detail || 'Failed to delete file.');
          });
        }
      })
      .then(() => {
        this.loadFiles();
      })
      .catch((e) => {
        console.error('Delete Error:', e);
        this.error = e.message || 'An unknown error occurred during deletion.';
        this.loading = false;
      });
  },

  // --- Utility Functions for Formatting ---
  formatSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  },

  formatDate(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  },
  // --- End Utility Functions ---
}));
