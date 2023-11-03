(function ($) {

    function _show_qr() {
        const qr = document.querySelector("#app_qrcode_img");
        var r = new XMLHttpRequest();
        var url = '/app/get_url_qrcode?url=' + window.location.href;
        r.onload = function () {
            var imageUrl = 'data:image/png;base64,' + r.response;
            if (qr) {
                qr.querySelector('img.qr-code').setAttribute('src', imageUrl);
                qr.classList.remove('d-none');
            }
        };
        r.open('GET', url, false);
        r.send();
    }

    function _hide_qr() {
        const qr = document.querySelector("#app_qrcode_img");
        if (qr) {
            qr.classList.add('d-none');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        //begin 处理二维码
        //纯 js 处理，便于给静态页面增加功能
        const qr_toggle = document.querySelector('#app_qrcode.footer_qrcode_container .fa-qrcode');

        // 使用 js 生成二维码更快，或者页面加载时就已有此二维码hide，然后 mouseover时 show
        if (qr_toggle) {
            qr_toggle.addEventListener('mouseover', function () {
                _show_qr();
            });

            qr_toggle.addEventListener('mouseout', function () {
                _hide_qr();
            });

            qr_toggle.addEventListener('click', function () {
                const qr = document.querySelector("#app_qrcode_img");
                if (qr && (qr.style.display === 'none' || qr.classList.contains('d-none'))) {
                    _show_qr();
                } else {
                    _hide_qr();
                }
            });
        }
        //end 处理二维码

        //begin 启动后强制登录
        setTimeout(function () {
            if (window.location.href.indexOf('odooai') !== -1 || window.location.href.indexOf('odooapp') !== -1) {
                r.open('GET', '/wxa/odooai/user/detail');
                r.send();
            }
        }, 4000);
        //end 启动后强制登录

        const content = document.getElementById('o_content');

        let imageModalId = 0;
        content.querySelectorAll('img').forEach(image => {
            // Enforce the presence of the `img-fluid` class on all images.
            image.classList.add('img-fluid', 'img-thumbnail');

            // Add a modal to each image that does not explicitly block it and has no target.
            if (!image.classList.contains('o-no-modal') && image.parentElement.tagName !== 'A') {
                const modalContainer = document.createElement('div');
                modalContainer.innerHTML = `<div class="modal fade" id="modal-${imageModalId}">
                       <div class="modal-dialog modal-dialog-centered">
                         <div class="modal-content">
                           <div class="modal-header">
                              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                           </div>
                           <div class="modal-body">
                              <img src="${image.src}" alt="${image.alt}" class="o-no-modal img-fluid img-thumbnail"/>
                           </div>
                         </div>
                       </div>
                     </div>
                `;
                image.parentNode.append(modalContainer);
                image.setAttribute('data-bs-toggle', 'modal');
                image.setAttribute('data-bs-target', `#modal-${imageModalId}`);
                imageModalId++;
            }
        });

        // Make all external links open in a new tab by default.
        content.querySelectorAll('a.external').forEach(externalLink => {
            externalLink.setAttribute('target', '_blank');
        })
    });

})();
