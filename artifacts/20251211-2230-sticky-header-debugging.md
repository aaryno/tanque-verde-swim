
/* ============================================
   STICKY HEADER FIX
   Apply these styles to fix the three-tier sticky header issue
   ============================================ */

/* STEP 1: Remove overflow from body entirely */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    /* NO overflow-x property at all - this breaks sticky on Safari */
    /* If you need to prevent horizontal scroll, wrap content instead */
}

/* STEP 2: Main Navigation - NO !important flags */
#main-nav {
    background-color: var(--tvhs-primary);
    padding: 0.4rem 0.75rem;
    position: -webkit-sticky;  /* Safari prefix */
    position: sticky;
    top: 0;
    z-index: 1030;
    /* Force GPU layer to help Safari */
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
}

/* STEP 3: Quick Navigation Bar - NO !important flags */
.quick-nav {
    background-color: var(--tvhs-accent);
    padding: 0.25rem 0;
    position: -webkit-sticky;
    position: sticky;
    top: 48px;  /* Height of main-nav */
    z-index: 1025;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
}

/* STEP 4: Page header - LOWER z-index than quick-nav */
.page-header {
    background: linear-gradient(135deg, var(--tvhs-primary) 0%, var(--tvhs-accent) 100%);
    color: white;
    padding: 0.75rem 0;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    position: -webkit-sticky;
    position: sticky;
    top: 88px;  /* 48px (main-nav) + 40px (quick-nav) */
    z-index: 1015;  /* LOWER than quick-nav */
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
}

/* STEP 5: Hero header - FIX THE TRANSITION */
.hero-header {
    position: -webkit-sticky;
    position: sticky;
    top: 88px;  /* Same as page-header */
    z-index: 1015;
    /* CRITICAL: Only transition specific properties, NOT 'all' */
    transition: padding 0.3s ease, opacity 0.3s ease;
    /* DO NOT USE: transition: all 0.3s ease; */
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
    margin: 0;
}

.hero-expanded {
    padding: 2.5rem 0;
}

.hero-collapsed {
    padding: 0.5rem 0;
}

/* When hero is collapsed, show/hide the right content */
.hero-header.collapsed .hero-expanded {
    display: none;
}

.hero-header:not(.collapsed) .hero-collapsed {
    display: none;
}

/* ============================================
   MOBILE RESPONSIVE - Recalculate heights
   ============================================ */
@media (max-width: 576px) {
    #main-nav {
        padding: 0.3rem 0.5rem;
        /* Let height be natural, don't force it */
    }
    
    .quick-nav {
        top: 40px;  /* Approximate height of mobile main-nav */
        padding: 0.2rem 0;
    }
    
    .page-header,
    .hero-header {
        top: 76px;  /* 40px + 36px approximate */
        padding: 0.35rem 0;
    }
}

/* ============================================
   ALTERNATIVE: If you MUST prevent horizontal scroll
   Wrap your content instead of using body overflow
   ============================================ */
/*
.content-wrapper {
    overflow-x: clip;
}
*/

/* ============================================
   DEBUG HELPER: Add this temporarily to visualize
   ============================================ */
/*
#main-nav { outline: 2px solid red; }
.quick-nav { outline: 2px solid blue; }
.hero-header { outline: 2px solid green; }
*/