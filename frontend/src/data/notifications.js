import { createResource } from 'dontmanage-ui'

export let unreadNotifications = createResource({
  cache: 'Unread Notifications Count',
  url: 'gameplan.api.unread_notifications',
  initialData: 0,
  auto: true,
})
