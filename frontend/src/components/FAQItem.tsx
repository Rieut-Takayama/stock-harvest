import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import type { FAQ } from '@/types';

interface FAQItemProps {
  faq: FAQ;
  expanded: boolean;
  onChange: (isExpanded: boolean) => void;
}

export const FAQItem: React.FC<FAQItemProps> = ({ faq, expanded, onChange }) => {
  return (
    <Accordion
      expanded={expanded}
      onChange={(_, isExpanded) => onChange(isExpanded)}
      sx={{
        boxShadow: 'none',
        border: 'none',
        '&:before': { display: 'none' },
        '&.Mui-expanded': { margin: 0 }
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMore />}
        sx={{
          borderBottom: '1px solid #e2e8f0',
          '&:hover': {
            backgroundColor: '#f8fffe'
          },
          '& .MuiAccordionSummary-content': {
            margin: '16px 0'
          }
        }}
      >
        <Typography variant="body1">
          Q. {faq.question}
        </Typography>
      </AccordionSummary>
      <AccordionDetails
        sx={{
          borderBottom: '1px solid #e2e8f0',
          pt: 0,
          pb: 2
        }}
      >
        <Typography variant="body2" color="text.secondary">
          {faq.answer}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );
};