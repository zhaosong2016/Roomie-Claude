// app.js
App({
  globalData: {
    apiUrl: 'http://49.233.127.228:5000',  // 后端API地址
    groupCode: '',  // 当前群口令
    userInfo: null,
    openid: ''  // 用户openid
  },

  onLaunch() {
    console.log('小程序启动')
    // 启用微信登录
    this.doLogin()
  },

  // 微信登录
  doLogin() {
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送code到后端换取openid
          wx.request({
            url: `${this.globalData.apiUrl}/api/login`,
            method: 'POST',
            header: {
              'content-type': 'application/json'
            },
            data: { code: res.code },
            timeout: 10000,
            success: (response) => {
              if (response.data && response.data.success) {
                this.globalData.openid = response.data.openid
                console.log('登录成功，openid:', response.data.openid)
              } else {
                console.error('登录失败:', response.data ? response.data.message : '未知错误')
                wx.showToast({
                  title: '登录失败，请重试',
                  icon: 'none'
                })
              }
            },
            fail: (err) => {
              console.error('登录请求失败:', err)
              wx.showToast({
                title: '网络连接失败',
                icon: 'none'
              })
            }
          })
        } else {
          console.error('wx.login失败:', res.errMsg)
        }
      },
      fail: (err) => {
        console.error('wx.login调用失败:', err)
      }
    })
  }
})
