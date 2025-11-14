#!/usr/bin/env python3
"""
Shared time and date formatting utilities for swim records.
"""

import pandas as pd
import re


def format_time_display(time_str: str) -> str:
    """
    Format swim time for display.
    
    Rules:
    - Two decimal places on seconds (52.68 not 52.6)
    - Remove leading zeros (56.59 not 00:56.59)
    - Remove minutes if under 1:00 (56.59 not 0:56.59)
    - Times should be right-justified in tables
    
    Examples:
        01:00.60 → 1:00.60
        00:56.59 → 56.59
        52.68 → 52.68
        52.6 → 52.60
    """
    if not time_str or pd.isna(time_str):
        return "—"
    
    time_str = str(time_str).strip()
    
    # Parse time to ensure 2 decimal places
    # Try to parse MM:SS.SS or SS.SS format
    if ':' in time_str:
        # Format: MM:SS.SS
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes = parts[0]
            seconds = parts[1]
            
            # Ensure seconds has 2 decimal places
            if '.' in seconds:
                sec_parts = seconds.split('.')
                if len(sec_parts[1]) < 2:
                    seconds = f"{sec_parts[0]}.{sec_parts[1]:0<2}"
            else:
                seconds = f"{seconds}.00"
            
            # Remove leading zero from minutes
            minutes = minutes.lstrip('0') or '0'
            
            # If minutes is 0, just return seconds
            if minutes == '0':
                return seconds
            
            return f"{minutes}:{seconds}"
    else:
        # Format: SS.SS (no minutes)
        if '.' in time_str:
            sec_parts = time_str.split('.')
            # Ensure 2 decimal places
            if len(sec_parts) == 2:
                if len(sec_parts[1]) < 2:
                    time_str = f"{sec_parts[0]}.{sec_parts[1]:0<2}"
        else:
            time_str = f"{time_str}.00"
    
    return time_str


def format_date_display(date_value) -> str:
    """
    Format date for display (without time component).
    
    Examples:
        2024-09-14 → Sep 14, 2024
        2024-09-14 00:00:00 → Sep 14, 2024
    """
    if pd.isna(date_value):
        return "—"
    
    try:
        date_obj = pd.to_datetime(date_value)
        return date_obj.strftime('%b %d, %Y')
    except:
        return str(date_value)

