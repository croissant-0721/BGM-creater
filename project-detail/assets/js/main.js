// ============================================ //
// 项目详情页面 JavaScript                       //
// ============================================ //

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化主题
    initTheme();

    // 初始化标签页
    initTabs();

    // 初始化搜索功能
    initSearch();

    // 初始化表单
    initForms();
});

// ============================================ //
// 主题切换功能                                  //
// ============================================ //

function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // 从 localStorage 获取保存的主题
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    themeToggle.checked = savedTheme === 'light';

    // 监听主题切换
    themeToggle.addEventListener('change', function() {
        const newTheme = this.checked ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// ============================================ //
// 标签页切换功能                                //
// ============================================ //

function initTabs() {
    // 默认激活第一个标签页
    const firstTab = document.querySelector('.tab[data-tab="scripts"]');
    if (firstTab) {
        switchTab('scripts');
    }
}

function switchTab(tabName) {
    // 移除所有标签页的激活状态
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('tab-active');
    });

    // 隐藏所有标签页内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });

    // 激活当前标签页
    const activeTab = document.querySelector(`.tab[data-tab="${tabName}"]`);
    if (activeTab) {
        activeTab.classList.add('tab-active');
    }

    // 显示当前标签页内容
    const activeContent = document.getElementById(`${tabName}-content`);
    if (activeContent) {
        activeContent.classList.remove('hidden');
    }
}

// ============================================ //
// 搜索功能                                     //
// ============================================ //

function initSearch() {
    // 为所有搜索输入框添加事件监听
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const tabContent = e.target.closest('.tab-content');

            if (tabContent) {
                filterItems(tabContent, searchTerm);
            }
        });
    });
}

function filterItems(container, searchTerm) {
    // 过滤表格行
    const tableRows = container.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });

    // 过滤卡片
    const cards = container.querySelectorAll('.card');
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// ============================================ //
// 模态框功能                                   //
// ============================================ //

function showAddScriptModal() {
    const modal = document.getElementById('add_script_modal');
    if (modal) {
        modal.showModal();
    }
}

function showAddCharacterModal() {
    const modal = document.getElementById('add_character_modal');
    if (modal) {
        modal.showModal();
    }
}

function showAddSceneModal() {
    // TODO: 实现场景添加模态框
    alert('新增场景功能开发中...');
}

function showAddItemModal() {
    // TODO: 实现物品添加模态框
    alert('新增物品功能开发中...');
}

function showAddVideoModal() {
    const modal = document.getElementById('add_video_modal');
    if (modal) {
        modal.showModal();
    }
}

function showAddVoiceoverModal() {
    const modal = document.getElementById('add_voiceover_modal');
    if (modal) {
        modal.showModal();
    }
}

// ============================================ //
// 表单处理                                     //
// ============================================ //

function initForms() {
    // 剧本表单
    const scriptForm = document.getElementById('addScriptForm');
    if (scriptForm) {
        scriptForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleScriptSubmit(this);
        });
    }

    // 文件输入框处理
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            handleFileSelect(e.target);
        });
    });

    // 图片URL粘贴处理
    const urlInputs = document.querySelectorAll('input[type="text"][placeholder*="URL"]');
    urlInputs.forEach(input => {
        input.addEventListener('paste', function(e) {
            handleImagePaste(e);
        });
    });
}

function handleScriptSubmit(form) {
    // 收集表单数据
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // TODO: 发送数据到后端
    console.log('创建剧本:', data);

    // 关闭模态框
    const modal = document.getElementById('add_script_modal');
    if (modal) {
        modal.close();
    }

    // 显示成功消息
    showNotification('剧本创建成功！', 'success');

    // 重置表单
    form.reset();
}

function handleFileSelect(input) {
    const file = input.files[0];
    if (file) {
        const urlInput = input.closest('.join, .form-control')?.querySelector('input[type="text"]');
        if (urlInput) {
            urlInput.value = file.name;
        }
    }
}

function handleImagePaste(event) {
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile();
            event.target.value = `[图片文件: ${blob.name}]`;
            event.preventDefault();
            break;
        }
    }
}

// ============================================ //
// 通知功能                                     //
// ============================================ //

function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} shadow-lg fixed top-20 right-4 z-[100] fade-in`;
    notification.innerHTML = `
        <div>
            <span>${message}</span>
        </div>
    `;

    // 添加到页面
    document.body.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ============================================ //
// 数据加载功能                                 //
// ============================================ //

function loadScripts() {
    // TODO: 从后端加载剧本列表
    console.log('加载剧本列表...');
}

function loadCharacters() {
    // TODO: 从后端加载角色列表
    console.log('加载角色列表...');
}

function loadScenes() {
    // TODO: 从后端加载场景列表
    console.log('加载场景列表...');
}

function loadItems() {
    // TODO: 从后端加载物品列表
    console.log('加载物品列表...');
}

function loadVideos() {
    // TODO: 从后端加载视频列表
    console.log('加载视频列表...');
}

function loadVoiceovers() {
    // TODO: 从后端加载配音列表
    console.log('加载配音列表...');
}

// ============================================ //
// 详情查看功能                                 //
// ============================================ //

function viewScriptDetail(scriptId) {
    // TODO: 实现剧本详情查看
    console.log('查看剧本详情:', scriptId);
    showNotification('剧本详情功能开发中...', 'info');
}

function viewCharacterDetail(characterId) {
    // TODO: 实现角色详情查看
    console.log('查看角色详情:', characterId);
    showNotification('角色详情功能开发中...', 'info');
}

function viewVideoDetail(videoId) {
    // TODO: 实现视频详情查看
    console.log('查看视频详情:', videoId);
    showNotification('视频详情功能开发中...', 'info');
}

// ============================================ //
// 删除功能                                     //
// ============================================ //

function deleteScript(scriptId) {
    if (confirm('确定要删除这个剧本吗？此操作不可撤销。')) {
        // TODO: 发送删除请求到后端
        console.log('删除剧本:', scriptId);
        showNotification('剧本已删除', 'success');
    }
}

function deleteCharacter(characterId) {
    if (confirm('确定要删除这个角色吗？此操作不可撤销。')) {
        // TODO: 发送删除请求到后端
        console.log('删除角色:', characterId);
        showNotification('角色已删除', 'success');
    }
}

function deleteVideo(videoId) {
    if (confirm('确定要删除这个视频吗？此操作不可撤销。')) {
        // TODO: 发送删除请求到后端
        console.log('删除视频:', videoId);
        showNotification('视频已删除', 'success');
    }
}

function deleteVoiceover(voiceoverId) {
    if (confirm('确定要删除这个配音吗？此操作不可撤销。')) {
        // TODO: 发送删除请求到后端
        console.log('删除配音:', voiceoverId);
        showNotification('配音已删除', 'success');
    }
}

// ============================================ //
// 刷新功能                                     //
// ============================================ //

function refreshCurrentTab() {
    const activeTab = document.querySelector('.tab-active');
    if (activeTab) {
        const tabName = activeTab.getAttribute('data-tab');
        switch(tabName) {
            case 'scripts':
                loadScripts();
                break;
            case 'characters':
                loadCharacters();
                break;
            case 'scenes':
                loadScenes();
                break;
            case 'items':
                loadItems();
                break;
            case 'fusion':
                // TODO: 加载融合生图列表
                break;
            case 'videos':
                loadVideos();
                break;
            case 'voiceovers':
                loadVoiceovers();
                break;
        }
    }
    showNotification('数据已刷新', 'success');
}

// ============================================ //
// 快捷键支持                                   //
// ============================================ //

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: 快速搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const activeSearch = document.querySelector('.tab-content:not(.hidden) input[type="search"]');
        if (activeSearch) {
            activeSearch.focus();
        }
    }

    // Ctrl/Cmd + N: 新建
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const activeTab = document.querySelector('.tab-active');
        if (activeTab) {
            const tabName = activeTab.getAttribute('data-tab');
            switch(tabName) {
                case 'scripts':
                    showAddScriptModal();
                    break;
                case 'characters':
                    showAddCharacterModal();
                    break;
                case 'videos':
                    showAddVideoModal();
                    break;
                case 'voiceovers':
                    showAddVoiceoverModal();
                    break;
            }
        }
    }

    // ESC: 关闭模态框
    if (e.key === 'Escape') {
        const openModal = document.querySelector('dialog[open]');
        if (openModal) {
            openModal.close();
        }
    }
});

// ============================================ //
// 导出功能（供外部调用）                        //
// ============================================ //

window.ProjectDetail = {
    switchTab,
    showAddScriptModal,
    showAddCharacterModal,
    showAddSceneModal,
    showAddItemModal,
    showAddVideoModal,
    showAddVoiceoverModal,
    refreshCurrentTab,
    viewScriptDetail,
    viewCharacterDetail,
    viewVideoDetail,
};
