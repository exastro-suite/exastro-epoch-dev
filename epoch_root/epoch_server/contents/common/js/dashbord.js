$(function(){
    // CommonAuth.onAuthSuccess(() => {
    //     console.log("dashbord.js : login scceed!!");
    // });
    $("#argocd_link").on("click",() => {
        console.log("#argocd_link click")
        window.location = "/_/argocd/direct_sso_login?organization_id=" + TESTgetRealm() + "&argocd_url=" + encodeURIComponent(window.location.origin + "/_/argocd/user-info");
    });
    function TESTgetRealm() {
        try {
            return CommonAuth.getRealm();
        } catch {
            return window.location.pathname.split("/")[1];
        }
    }
    //document.cookie = "argocd.oauthstate=; max-age=0;";
    //document.cookie = "argocd.token=; max-age=0;";
})
