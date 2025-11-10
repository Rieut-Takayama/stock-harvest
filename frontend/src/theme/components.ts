import type { Components, Theme } from '@mui/material/styles';

/**
 * ナチュラルライトテーマ - コンポーネントスタイル定義
 * ソフトなシャドウと自然な色合いで上品な印象を演出
 * 株式投資アプリに最適化されたコンポーネント設定
 */
export const naturalLightComponents: Components<Omit<Theme, 'components'>> = {
  // ボタンコンポーネント
  MuiButton: {
    styleOverrides: {
      root: ({ ownerState }) => ({
        borderRadius: 8,
        textTransform: 'none',
        fontWeight: 600,
        padding: '10px 20px',
        boxShadow: 'none',
        transition: 'all 0.2s ease-in-out',
        
        '&:hover': {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          transform: 'translateY(-1px)',
        },
        
        '&:active': {
          transform: 'translateY(0)',
        },
        
        ...(ownerState.size === 'large' && {
          padding: '12px 24px',
          fontSize: '1rem',
        }),
        
        ...(ownerState.size === 'small' && {
          padding: '6px 16px',
          fontSize: '0.875rem',
        }),
      }),
      
      contained: () => ({
        background: 'linear-gradient(135deg, #38a169 0%, #68d391 100%)',
        color: '#ffffff',
        
        '&:hover': {
          background: 'linear-gradient(135deg, #2f855a 0%, #48bb78 100%)',
          boxShadow: '0 4px 12px rgba(56, 161, 105, 0.3)',
        },
        
        '&:disabled': {
          background: '#e2e8f0',
          color: '#a0aec0',
        },
      }),
      
      outlined: () => ({
        borderColor: '#38a169',
        color: '#38a169',
        borderWidth: 2,
        
        '&:hover': {
          borderColor: '#2f855a',
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
      }),
      
      text: () => ({
        color: '#38a169',
        
        '&:hover': {
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
      }),
    },
  },

  // カードコンポーネント
  MuiCard: {
    styleOverrides: {
      root: () => ({
        borderRadius: 12,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e2e8f0',
        transition: 'all 0.2s ease-in-out',
        
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.08)',
          transform: 'translateY(-2px)',
        },
      }),
    },
  },

  // チップコンポーネント
  MuiChip: {
    styleOverrides: {
      root: ({ ownerState }) => ({
        borderRadius: 16,
        fontWeight: 500,
        fontSize: '0.75rem',
        height: 28,
        
        ...(ownerState.color === 'primary' && {
          backgroundColor: '#edf7ed',
          color: '#38a169',
          border: '1px solid #c6f6d5',
        }),
        
        ...(ownerState.variant === 'outlined' && {
          borderWidth: 1,
        }),
      }),
      
      // 株価変動用のカスタムスタイル
      colorSuccess: {
        backgroundColor: '#edf7ed',
        color: '#38a169',
        border: '1px solid #c6f6d5',
      },
      
      colorError: {
        backgroundColor: '#fed7d7',
        color: '#e53e3e',
        border: '1px solid #feb2b2',
      },
    },
  },

  // アプリバー
  MuiAppBar: {
    styleOverrides: {
      root: () => ({
        backgroundColor: '#ffffff',
        color: '#2d3748',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
        borderBottom: '1px solid #e2e8f0',
      }),
    },
  },

  // ツールバー
  MuiToolbar: {
    styleOverrides: {
      root: {
        minHeight: 64,
        padding: '0 24px',
      },
    },
  },

  // ペーパーコンポーネント
  MuiPaper: {
    styleOverrides: {
      root: () => ({
        backgroundColor: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e2e8f0',
      }),
      
      elevation1: {
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
      },
      
      elevation2: {
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.08)',
      },
      
      elevation3: {
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08)',
      },
    },
  },

  // インプットベース
  MuiInputBase: {
    styleOverrides: {
      root: () => ({
        borderRadius: 8,
        backgroundColor: '#ffffff',
        border: '1px solid #e2e8f0',
        transition: 'all 0.2s ease-in-out',
        
        '&:hover': {
          borderColor: '#c6f6d5',
        },
        
        '&.Mui-focused': {
          borderColor: '#38a169',
          boxShadow: '0 0 0 3px rgba(56, 161, 105, 0.1)',
        },
      }),
    },
  },

  // アウトライン入力
  MuiOutlinedInput: {
    styleOverrides: {
      root: () => ({
        '& .MuiOutlinedInput-notchedOutline': {
          borderColor: '#e2e8f0',
          borderWidth: 1,
        },
        
        '&:hover .MuiOutlinedInput-notchedOutline': {
          borderColor: '#c6f6d5',
        },
        
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
          borderColor: '#38a169',
          borderWidth: 2,
        },
      }),
    },
  },

  // テーブル
  MuiTableHead: {
    styleOverrides: {
      root: () => ({
        backgroundColor: '#f7fafc',
        
        '& .MuiTableCell-head': {
          fontWeight: 600,
          color: '#2d3748',
          borderBottom: '2px solid #e2e8f0',
        },
      }),
    },
  },

  MuiTableCell: {
    styleOverrides: {
      root: () => ({
        borderBottom: '1px solid #e2e8f0',
        padding: '12px 16px',
      }),
      
      head: {
        fontWeight: 600,
        backgroundColor: '#f7fafc',
      },
    },
  },

  MuiTableRow: {
    styleOverrides: {
      root: () => ({
        '&:hover': {
          backgroundColor: '#f7fafc',
        },
        
        '&.Mui-selected': {
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
      }),
    },
  },

  // タブ
  MuiTabs: {
    styleOverrides: {
      root: {
        minHeight: 48,
        borderBottom: '1px solid #e2e8f0',
      },
      
      indicator: {
        backgroundColor: '#38a169',
        height: 3,
        borderRadius: '3px 3px 0 0',
      },
    },
  },

  MuiTab: {
    styleOverrides: {
      root: () => ({
        textTransform: 'none',
        fontWeight: 500,
        fontSize: '0.875rem',
        color: '#4a5568',
        minHeight: 48,
        padding: '12px 16px',
        
        '&.Mui-selected': {
          color: '#38a169',
          fontWeight: 600,
        },
        
        '&:hover': {
          color: '#38a169',
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
      }),
    },
  },

  // アイコンボタン
  MuiIconButton: {
    styleOverrides: {
      root: () => ({
        borderRadius: 8,
        padding: 8,
        transition: 'all 0.2s ease-in-out',
        
        '&:hover': {
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
          transform: 'scale(1.05)',
        },
      }),
    },
  },

  // リストアイテム
  MuiListItemButton: {
    styleOverrides: {
      root: () => ({
        borderRadius: 8,
        margin: '2px 8px',
        padding: '8px 16px',
        
        '&:hover': {
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
        
        '&.Mui-selected': {
          backgroundColor: 'rgba(56, 161, 105, 0.08)',
          color: '#38a169',
          
          '&:hover': {
            backgroundColor: 'rgba(56, 161, 105, 0.12)',
          },
        },
      }),
    },
  },

  // スイッチ
  MuiSwitch: {
    styleOverrides: {
      root: {
        width: 42,
        height: 26,
        padding: 0,
        display: 'flex',
      },
      
      switchBase: () => ({
        padding: 1,
        '&.Mui-checked': {
          color: '#ffffff',
          transform: 'translateX(16px)',
          '& + .MuiSwitch-track': {
            backgroundColor: '#38a169',
            opacity: 1,
            border: 'none',
          },
        },
      }),
      
      track: {
        borderRadius: 13,
        border: '1px solid #e2e8f0',
        backgroundColor: '#cbd5e0',
        opacity: 1,
        transition: 'background-color 0.2s ease-in-out',
      },
      
      thumb: {
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
        width: 24,
        height: 24,
      },
    },
  },

  // アラート
  MuiAlert: {
    styleOverrides: {
      root: () => ({
        borderRadius: 8,
        padding: '12px 16px',
      }),
      
      standardSuccess: {
        backgroundColor: '#edf7ed',
        color: '#38a169',
        border: '1px solid #c6f6d5',
        
        '& .MuiAlert-icon': {
          color: '#38a169',
        },
      },
      
      standardError: {
        backgroundColor: '#fed7d7',
        color: '#e53e3e',
        border: '1px solid #feb2b2',
        
        '& .MuiAlert-icon': {
          color: '#e53e3e',
        },
      },
      
      standardWarning: {
        backgroundColor: '#fef5e7',
        color: '#d69e2e',
        border: '1px solid #f6e05e',
        
        '& .MuiAlert-icon': {
          color: '#d69e2e',
        },
      },
      
      standardInfo: {
        backgroundColor: '#ebf8ff',
        color: '#3182ce',
        border: '1px solid #90cdf4',
        
        '& .MuiAlert-icon': {
          color: '#3182ce',
        },
      },
    },
  },

  // ダイアログ
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 12,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
      },
    },
  },

  // メニュー
  MuiMenu: {
    styleOverrides: {
      paper: {
        borderRadius: 8,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        border: '1px solid #e2e8f0',
      },
    },
  },

  MuiMenuItem: {
    styleOverrides: {
      root: () => ({
        padding: '8px 16px',
        borderRadius: 6,
        margin: '2px 4px',
        
        '&:hover': {
          backgroundColor: 'rgba(56, 161, 105, 0.04)',
        },
        
        '&.Mui-selected': {
          backgroundColor: 'rgba(56, 161, 105, 0.08)',
          
          '&:hover': {
            backgroundColor: 'rgba(56, 161, 105, 0.12)',
          },
        },
      }),
    },
  },
};