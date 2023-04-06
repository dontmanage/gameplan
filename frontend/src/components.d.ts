// defining global components here for autocompletion via volar
// https://github.com/johnsoncodehk/volar/tree/master/extensions/vscode-vue-language-features

declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    RouterLink: typeof import('vue-router')['RouterLink']
    RouterView: typeof import('vue-router')['RouterView']
    Button: typeof import('dontmanage-ui')['Button']
    Input: typeof import('dontmanage-ui')['Input']
    ErrorMessage: typeof import('dontmanage-ui')['ErrorMessage']
    Dialog: typeof import('dontmanage-ui')['Dialog']
    FeatherIcon: typeof import('dontmanage-ui')['FeatherIcon']
    Alert: typeof import('dontmanage-ui')['Alert']
    Badge: typeof import('dontmanage-ui')['Badge']
    UserInfo: typeof import('dontmanage-ui')['UserInfo']
    UserAvatar: typeof import('./components/UserAvatar.vue')
  }
}

export {}
