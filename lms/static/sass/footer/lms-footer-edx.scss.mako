// Footer for edx.org (right-to-left)
// ==================================

// libs and resets *do not edit*
@import 'bourbon/bourbon'; // lib - bourbon
@import 'vendor/bi-app/bi-app-ltr'; // set the layout for left to right languages

// base - utilities
@import 'base/variables';
@import 'base/mixins';

// base - assets
@import 'base/font_face';

footer#footer-edx-v3 {
    @import 'base/extends';

    // base - starter
    @import 'base/base';
}

// base - elements
@import 'elements/typography';

// shared - platform
@import 'shared/footer-edx';
