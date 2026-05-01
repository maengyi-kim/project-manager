const api = require('../../utils/api');

Page({
  data: {
    stats: {
      total_projects: 0,
      active_projects: 0,
      completed_projects: 0,
      overdue_projects: 0,
      total_overdue_tasks: 0
    },
    projects: []
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    try {
      const [stats, projects] = await Promise.all([
        api.getOverview(),
        api.getProjects()
      ]);
      this.setData({ stats, projects });
    } catch (err) {
      console.error('加载统计失败:', err);
    }
  },

  statusText(s) {
    const map = { active: '进行中', paused: '暂停', completed: '已完成', cancelled: '已取消' };
    return map[s] || s;
  },

  onOpen(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/project/project?id=${id}` });
  }
});
