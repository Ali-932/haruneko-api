import NodeBloatGuard from './node/BloatGuard';

export interface IBloatGuard {
    Initialize(): Promise<void>;
}

export function CreateBloatGuard(): IBloatGuard {
    // API-only mode: always use Node bloat guard
    return new NodeBloatGuard();
}

// Sort: https://www.online-utility.org/text/sort.jsp
const patterns = [
    '*://*.21wiz.com/*',
    '*://*.4dex.io/*',
    '*://*.a-ads.com/*',
    '*://*.adskeeper.co.uk/*',
    '*://*.adskeeper.com/*',
    '*://*.arc.io/*',
    '*://*.bidgear.com/*',
    '*://*.chatango.com/*',
    '*://*.clokemidriff.com/*',
    '*://*.doubleclick.net/*',
    '*://*.google-analytics.com/*',
    '*://*.googlesyndication.com/*',
    '*://itchyshavecommand.com/*',
    '*://*.magsrv.com/*',
    '*://*.mgid.com/*',
    '*://*.onesignal.com/*',
    '*://*.ospicalad.buzz/*',
    '*://*.outbrain.com/*',
    '*://*.outbrainimg.com/*',
    '*://*.papayads.net/*',
    '*://*.profitableratecpm.com/',
    '*://*.prplads.com/*',
    '*://*.pubadx.one/*',
    '*://*.pubfuture-ad.com/*',
    '*://*.purpleads.io/*',
    '*://*.sentry.io/*',
    '*://*.sharethis.com/*',
    '*://*.topcreativeformat.com/*',
    '*://*.twitch.tv/*',
    '*://*.yandex.ru/*.js',
    '*://*/**/devtools-detect*',
    '*://*/**/devtools-detector*',
    '*://*/**/disable-devtool*',
    '*://*/Ads/*',
    '*://*/js/ads*',
    '*://breathinggeoff.com/*',
    '*://captivatepestilentstormy.com/*',
    '*://creepingbrings.com/*',
    '*://crunchyscan.fr/arc-sw?*',
    '*://crunchyscan.fr/arc-widget',
    '*://crunchyscan.fr/blockexx.js',
    '*://fireworksane.com/*',
    '*://fleraprt.com/*',
    '*://goomaphy.com/*',
    '*://kettledroopingcontinuation.com/*',
    '*://obqj2.com/',
    '*://owewary.com/*',
    '*://pickupfaxmultitude.com/*',
    '*://pliantdummyexasperation.com/*',
    '*://preferencenail.com/*',
    '*://stoampaliy.net/*',
    '*://t7cp4fldl.com/*',
    '*://tattedly.com/*',
    '*://tqqbhtnshynrypl.xyz/*',
    '*://tumultmarten.com/*',
    '*://valuerabjure.com/*',
    '*://voltoishime.top/*',
    '*://www.facebook.com/*/plugins/comments.php*',
    '*://www.facebook.net/*/plugins/comments.php*'
];