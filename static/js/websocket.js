// const notificationSocket = new WebSocket(
//     'ws://' + window.location.host + '/ws/notifications/'
// );

// notificationSocket.onopen=function(e){
//     alert('con');
// }


// notificationSocket.onmessage = function(e) {
//     alert('message');
//     if (Notification.permission === 'granted') {
//         new Notification('إشعار جديد', {
//             body: 'data.message', // نص الإشعار
//             //icon: '/static/images/notification-icon.png', // اختياري: صورة الإشعار
//         });
//           // إضافة حدث عند النقر على الإشعار
//           notification.onclick = function() {
//             // الانتقال إلى الرابط الخاص بالإشعار
//             window.open(data.url, '_blank'); // فتح الرابط في نافذة جديدة
//           }
        
//     }

//     const data = JSON.parse(e.data);
//     console.log('onmessage');
//     if (data.type === 'notification') {
//         const notification = data.notification;
        
//         // تحديث عدد الإشعارات غير المقروءة
//         const countElement = $('#notification-count');
//         const currentCount = parseInt(countElement.text()) || 0;
//         countElement.text(currentCount + 1).show();
        
//         // إضافة الإشعار الجديد إلى القائمة المنسدلة
//         const notificationHtml = `
//             <a href="#" class="dropdown-item notification-item unread">
//                 <div class="d-flex align-items-center">
//                     <div class="flex-shrink-0">
//                         <img src="${notification.sender.avatar_url || '/static/img/default-avatar.png'}" 
//                              class="rounded-circle" 
//                              width="32" height="32" 
//                              alt="${notification.sender.name}">
//                     </div>
//                     <div class="flex-grow-1 ms-2">
//                         <p class="mb-0">${notification.text}</p>
//                         <small class="text-muted">${notification.created_at}</small>
//                     </div>
//                 </div>
//             </a>
//         `;
        
//         $('.notifications-dropdown .dropdown-menu').prepend(notificationHtml);
        
//         // إظهار إشعار منبثق
//         const toast = `
//             <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
//                 <div class="toast-header">
//                     <img src="${notification.sender.avatar_url || '/static/img/default-avatar.png'}" 
//                          class="rounded me-2" 
//                          width="20" height="20" 
//                          alt="${notification.sender.name}">
//                     <strong class="me-auto">إشعار جديد</strong>
//                     <small class="text-muted">الآن</small>
//                     <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
//                 </div>
//                 <div class="toast-body">
//                     ${notification.text}
//                 </div>
//             </div>
//         `;
        
//         const toastContainer = $('<div class="toast-container position-fixed top-0 end-0 p-3"></div>');
//         toastContainer.html(toast);
//         $('body').append(toastContainer);
        
//         const toastElement = $('.toast').last();
//         const bsToast = new bootstrap.Toast(toastElement);
//         bsToast.show();
        
//         // تشغيل صوت الإشعار
//         const notificationSound = new Audio('/static/notifications/notification.mp3');
//         notificationSound.play();
//     }
// };
//  /*
// notificationSocket.onclose = function(e) {
//     console.error('Notification socket closed unexpectedly');
// };

// */