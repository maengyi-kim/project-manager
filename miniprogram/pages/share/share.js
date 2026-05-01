const api = require('../../utils/api');

Page({
  data: {
    project: {},
    tasks: [],
  },

  onLoad(options) {
    // 从链接参数获取项目ID
    const id = options.id;
    if (id) {
      this.loadProject(id);
    }
  },

  async loadProject(id) {
    try {
      const data = await api.shareProject(id);
      this.setData({ project: data, tasks: data.tasks || [] });
      wx.setNavigationBarTitle({ title: data.name || '项目进度' });
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  taskDepth(item) {
    return item.depth || 0;
  }
});
