// function ocultar(){
// 	document.getElementById("img").style.display = "no"
// }
// Referencia
// https://www.youtube.com/watch?v=KJbLiV6Y9sY


document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      $notification.parentNode.removeChild($notification);
    });
  });
});