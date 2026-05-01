App({
  globalData: {
    baseUrl: 'https://pm.maengyi.top',
    userInfo: null,
    isVisitor: false  // true=只看模式
  },

  onLaunch() {
    // 检查是否从分享链接进入（只看模式）
    const query = wx.getEnterOptionsSync().query || {};
    if (query.share === '1') {
      this.globalData.isVisitor = true;
    }
  }
})
