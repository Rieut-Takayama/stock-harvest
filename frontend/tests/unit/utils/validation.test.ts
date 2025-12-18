import { describe, it, expect } from 'vitest'

// バリデーション関数のサンプル実装
function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

function isValidStockCode(code: string): boolean {
  // 日本の株式コード（4桁の数字）
  const stockCodeRegex = /^\d{4}$/
  return stockCodeRegex.test(code)
}

function formatPrice(price: number): string {
  return price.toLocaleString('ja-JP', {
    style: 'currency',
    currency: 'JPY'
  })
}

describe('Validation Utils', () => {
  describe('isValidEmail', () => {
    it('有効なメールアドレスを正しく判定する', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name@domain.co.jp')).toBe(true)
    })

    it('無効なメールアドレスを正しく判定する', () => {
      expect(isValidEmail('')).toBe(false)
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('test@')).toBe(false)
      expect(isValidEmail('@domain.com')).toBe(false)
    })
  })

  describe('isValidStockCode', () => {
    it('有効な株式コードを正しく判定する', () => {
      expect(isValidStockCode('7203')).toBe(true)
      expect(isValidStockCode('9984')).toBe(true)
    })

    it('無効な株式コードを正しく判定する', () => {
      expect(isValidStockCode('')).toBe(false)
      expect(isValidStockCode('123')).toBe(false)
      expect(isValidStockCode('12345')).toBe(false)
      expect(isValidStockCode('ABCD')).toBe(false)
    })
  })

  describe('formatPrice', () => {
    it('価格を正しく日本円形式でフォーマットする', () => {
      expect(formatPrice(1000)).toBe('￥1,000')
      expect(formatPrice(1234567)).toBe('￥1,234,567')
      expect(formatPrice(0)).toBe('￥0')
    })
  })
})