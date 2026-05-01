const api = require('../../utils/api');

Page({
  data: {
    projects: [],
    activeCount: 0,
    overdueCount: 0
  },

  onShow() {
    this.loadProjects();
  },

  onPullDownRefresh() {
    this.loadProjects().then(() => wx.stopPullDownRefresh());
  },

  async loadProjects() {
    try {
      const projects = await api.getProjects();
      const activeCount = projects.filter(p => p.status === 'active').length;
      const overdueCount = projects.reduce((sum, p) => sum + (p.overdue_count || 0), 0);

      this.setData({ projects, activeCount, overdueCount });
    } catch (err) {
      console.error('加载项目失败:', err);
    }
  },

  statusText(status) {
    const map = { active: '进行中', paused: '暂停', completed: '已完成', cancelled: '已取消' };
    return map[status] || status;
  },

  onOpenProject(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/project/project?id=${id}` });
  },

  onCreateProject() {
    wx.showModal({
      title: '新建项目',
      content: '输入项目名称',
      editable: true,
      placeholderText: '例如：食品厂净化改造',
      success: (res) => {
        if (res.confirm && res.content) {
          api.createProject({ name: res.content }).then(() => {
            this.loadProjects();
            wx.showToast({ title: '创建成功', icon: 'success' });
          });
        }
      }
    });
  }
});
