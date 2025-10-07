import Swal from 'sweetalert2';
import 'sweetalert2/src/sweetalert2.scss';

export const Notification = {
  success: (message, title = 'Éxito') => {
    return Swal.fire({
      icon: 'success',
      title: title,
      text: message,
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      background: '#f8f9fa',
      customClass: {
        popup: 'custom-swal-popup'
      }
    });
  },

  error: (message, title = 'Error') => {
    return Swal.fire({
      icon: 'error',
      title: title,
      text: message,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#d32f2f',
      background: '#f8f9fa'
    });
  },

  confirm: (message, title = 'Confirmar') => {
    return Swal.fire({
      icon: 'question',
      title: title,
      text: message,
      showCancelButton: true,
      confirmButtonText: 'Sí',
      cancelButtonText: 'No',
      confirmButtonColor: '#1976d2',
      cancelButtonColor: '#6c757d',
      background: '#f8f9fa'
    });
  },

  loading: (message = 'Procesando...') => {
    return Swal.fire({
      title: message,
      allowEscapeKey: false,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
      background: '#f8f9fa'
    });
  },

  close: () => {
    Swal.close();
  }
};