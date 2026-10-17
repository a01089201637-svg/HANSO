(function() {
    // 1. 스타일 정의 (배경색 White 및 UI 최적화)
    let styleTag = document.getElementById('ext-dynamic-style');
    if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = 'ext-dynamic-style';
        document.head.appendChild(styleTag);
    }
    styleTag.innerHTML = `
        /* 환경 설정 패널: 순백색 배경 적용 */
        #ext-panel-root {
            position: fixed; top: 20px; right: 80px; width: 320px;
            background: #ffffff; color: #333333; padding: 20px;
            border-radius: 15px; z-index: 10001; 
            display: none !important; /* 초기 상태 숨김 */
            max-height: 85vh; overflow-y: auto;
            border: 1px solid #e6e9ef;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            font-family: 'Apple SD Gothic Neo', sans-serif;
        }
        
        /* 활성화 상태 */
        #ext-panel-root.active { 
            display: block !important; 
            animation: extFadeIn 0.3s ease; 
        }

        @keyframes extFadeIn {
            from { opacity: 0; transform: translateX(30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* 토글 버튼 스타일 */
        #ext-toggle-btn {
            position: fixed; bottom: 20px; right: 20px;
            width: 50px; height: 50px; border-radius: 50%;
            background: #3498db; color: white; border: none;
            cursor: pointer; z-index: 10002; display: flex;
            align-items: center; justify-content: center; font-size: 22px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        #ext-toggle-btn:hover { transform: scale(1.1); background: #2980b9; }

        /* 내부 그룹 디자인 (기존 설정창과 동일하게) */
        .ext-group { 
            border: 1px solid #f0f2f5; 
            border-radius: 10px; 
            margin-bottom: 12px; 
            overflow: hidden; 
            background: #ffffff;
        }
        .ext-group-header { 
            background: #f8f9fb; 
            padding: 10px 12px; 
            font-weight: bold; 
            font-size: 13px; 
            color: #4a5568; 
            border-bottom: 1px solid #f0f2f5; 
        }
        .ext-group-content { padding: 12px; }
        
        /* 입력 요소 스타일 */
        .ext-input-label { font-size: 11px; color: #718096; display: block; margin-bottom: 4px; }
        .ext-color-picker { width: 100%; height: 30px; border: 1px solid #e2e8f0; border-radius: 5px; cursor: pointer; background: none; }
        
        /* 말풍선 변수 */
        .me-bubble { background-color: var(--me-bg) !important; color: var(--me-text) !important; }
        .other-bubble { background-color: var(--other-bg) !important; color: var(--other-text) !important; }
        
        .custom-sticker-obj { position: fixed; cursor: move; user-select: none; z-index: 9999; pointer-events: auto; }
    `;

    // 2. 패널 생성
    if (document.getElementById('ext-panel-root')) return;

    const panel = document.createElement('div');
    panel.id = 'ext-panel-root';
    panel.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom: 2px solid #f7fafc; padding-bottom: 10px;">
            <h3 style="margin:0; font-size:15px; color: #2d3748;">🎨 환경 설정</h3>
            <span id="ext-close-panel" style="cursor:pointer; font-size:24px; color: #a0aec0; line-height:1;">&times;</span>
        </div>
        
        <div class="ext-group">
            <div class="ext-group-header">배경 디자인</div>
            <div class="ext-group-content">
                <span class="ext-input-label">배경색 선택</span>
                <input type="color" id="ext-bg-color" value="#ffffff" class="ext-color-picker" style="margin-bottom:12px;">
                <span class="ext-input-label">배경 이미지 업로드</span>
                <input type="file" id="ext-bg-img" accept="image/*" style="font-size:11px; width:100%; color: #4a5568;">
            </div>
        </div>

        <div class="ext-group">
            <div class="ext-group-header">말풍선 테마</div>
            <div class="ext-group-content" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
                <div>
                    <p style="font-size:11px; margin:0 0 6px 0; text-align:center; font-weight:bold; color: #4a5568;">나 (Me)</p>
                    <input type="color" id="ext-me-bg" value="#007AFF" class="ext-color-picker">
                    <input type="color" id="ext-me-text" value="#ffffff" class="ext-color-picker" style="margin-top:4px;">
                </div>
                <div>
                    <p style="font-size:11px; margin:0 0 6px 0; text-align:center; font-weight:bold; color: #4a5568;">상대방</p>
                    <input type="color" id="ext-other-bg" value="#e5e5ea" class="ext-color-picker">
                    <input type="color" id="ext-other-text" value="#000000" class="ext-color-picker" style="margin-top:4px;">
                </div>
            </div>
        </div>

        <div class="ext-group">
            <div class="ext-group-header">스티커 관리</div>
            <div class="ext-group-content">
                <button id="ext-sticker-upload-btn" style="width:100%; cursor:pointer; background:#3498db; border:none; color:white; padding:10px; border-radius:8px; font-weight:bold; font-size:12px; transition: 0.2s;">🖼️ 새 스티커 추가</button>
                <input type="file" id="ext-sticker-file" accept="image/*" style="display:none;">
            </div>
        </div>
    `;
    document.body.appendChild(panel);

    // 3. 토글 버튼 생성
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'ext-toggle-btn';
    toggleBtn.innerHTML = '🎨';
    document.body.appendChild(toggleBtn);

    // 4. 로직 (토글 및 상호 배제)
    const toggleExtPanel = () => {
        if (window.closeBaseSettings) window.closeBaseSettings();
        panel.classList.toggle('active');
    };

    toggleBtn.onclick = (e) => { e.stopPropagation(); toggleExtPanel(); };
    document.getElementById('ext-close-panel').onclick = (e) => { e.stopPropagation(); panel.classList.remove('active'); };

    window.closeExtSettings = function() {
        panel.classList.remove('active');
    };

    // 5. 스타일 적용 함수
    const chatTarget = document.getElementById('chat-section') || document.querySelector('.chat-section');
    function applyStyles() {
        if (!chatTarget) return;
        chatTarget.style.backgroundColor = document.getElementById('ext-bg-color').value;
        document.documentElement.style.setProperty('--me-bg', document.getElementById('ext-me-bg').value);
        document.documentElement.style.setProperty('--me-text', document.getElementById('ext-me-text').value);
        document.documentElement.style.setProperty('--other-bg', document.getElementById('ext-other-bg').value);
        document.documentElement.style.setProperty('--other-text', document.getElementById('ext-other-text').value);
    }

    // 이벤트 리스너
    document.getElementById('ext-bg-img').onchange = function(e) {
        if (e.target.files[0] && chatTarget) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                chatTarget.style.backgroundImage = `url(${ev.target.result})`;
                chatTarget.style.backgroundSize = 'cover';
                chatTarget.style.backgroundPosition = 'center';
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    };

    document.getElementById('ext-sticker-upload-btn').onclick = () => document.getElementById('ext-sticker-file').click();
    document.getElementById('ext-sticker-file').onchange = function(e) {
        if (e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = (ev) => createSticker(ev.target.result);
            reader.readAsDataURL(e.target.files[0]);
            e.target.value = '';
        }
    };

    function createSticker(src) {
        const st = document.createElement('img');
        st.src = src;
        st.className = 'custom-sticker-obj';
        st.style.cssText = `left: 50vw; top: 50vh; width: 150px; transform: translate(-50%, -50%);`;
        st.oncontextmenu = (e) => { e.preventDefault(); st.remove(); };
        st.onmousedown = function(e) {
            if (e.button !== 0) return;
            e.preventDefault();
            const rect = st.getBoundingClientRect();
            st.style.transform = 'none';
            st.style.left = rect.left + 'px';
            st.style.top = rect.top + 'px';
            let shiftX = e.clientX - rect.left;
            let shiftY = e.clientY - rect.top;
            function moveAt(pageX, pageY) {
                st.style.left = (pageX - shiftX) + 'px';
                st.style.top = (pageY - shiftY) + 'px';
            }
            function onMouseMove(event) { moveAt(event.clientX, event.clientY); }
            document.addEventListener('mousemove', onMouseMove);
            document.onmouseup = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.onmouseup = null;
            };
        };
        document.body.appendChild(st);
    }

    ['ext-bg-color', 'ext-me-bg', 'ext-me-text', 'ext-other-bg', 'ext-other-text'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.oninput = applyStyles;
    });

    applyStyles();
})();