import apiService from './api.js'

export function isPushSupported() {
  return (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  )
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

async function getRegistration() {
  if (!('serviceWorker' in navigator)) {
    throw new Error('Service Worker не поддерживается')
  }
  return navigator.serviceWorker.ready
}

export async function getCurrentSubscription() {
  if (!isPushSupported()) return null
  try {
    const reg = await getRegistration()
    return await reg.pushManager.getSubscription()
  } catch {
    return null
  }
}

export async function subscribeToPush() {
  if (!isPushSupported()) {
    throw new Error('Push-уведомления не поддерживаются в этом браузере')
  }

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') {
    throw new Error('Разрешение на уведомления не получено')
  }

  const reg = await getRegistration()
  const existing = await reg.pushManager.getSubscription()
  if (existing) {
    // Уже подписаны локально — синхронизируем с бэкендом
    await apiService.subscribePush(existing.toJSON())
    return existing
  }

  const vapidKey = await apiService.getVapidPublicKey()
  if (!vapidKey) {
    throw new Error('VAPID-ключ не настроен на сервере')
  }

  const subscription = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidKey),
  })

  await apiService.subscribePush(subscription.toJSON())
  return subscription
}

export async function unsubscribeFromPush(endpoint) {
  if (!isPushSupported()) return

  try {
    if (endpoint) await apiService.unsubscribePush(endpoint)
  } catch (e) {
    console.warn('Backend unsubscribe failed:', e)
  }

  const reg = await getRegistration()
  const sub = await reg.pushManager.getSubscription()
  if (sub) await sub.unsubscribe()
}
