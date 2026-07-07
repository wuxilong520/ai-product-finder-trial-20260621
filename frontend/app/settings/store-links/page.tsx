import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, Button } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getAccountOverview } from "@/lib/api/account";
import { isAuthError } from "@/lib/api";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function StoreLinksPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();

  let overview;
  try {
    overview = await getAccountOverview(token);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }

  const shopify = overview.store_links.shopify;

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 店铺绑定</div>
          <h1 className="text-3xl font-semibold tracking-tight text-white">店铺绑定</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这个页面现在不再放空话，直接告诉你 Shopify 到底已经接到哪一步：真实读取、用户自助绑定、真实发布，分别到什么状态。
          </p>
        </Card>

        <div className="grid gap-6 xl:grid-cols-4">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>Shopify 读取状态</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前状态" value={shopify.status_text} />
              <InfoTile label="店铺地址参数" value={shopify.store_base_url_configured ? "已配置" : "未配置"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>读取能力</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="真实商品读取" value={shopify.admin_read_ready ? "已打开" : "未打开"} />
              <InfoTile label="当前说明" value={shopify.admin_read_ready ? "现在可以读取 Shopify 商品数据" : "当前还不能读取真实 Shopify 商品"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>绑定能力</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="用户自助绑定" value={shopify.oauth_status === "reserved" ? "结构已预留" : shopify.oauth_status} />
              <InfoTile label="当前结论" value="还没有收口成“你自己点一下就绑定成功”的最终形态" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>发布能力</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="执行模式" value={shopify.execution_mode} />
              <InfoTile label="真实发布" value={shopify.publish_text} />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>现在这页说真话</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {[
              shopify.admin_read_ready
                ? "你现在的 Shopify 真实读取参数已经配好，可以继续往市场分析和商品匹配方向使用。"
                : "你现在的 Shopify 真实读取参数还没配好，所以这里不会假装你已经能读到店铺数据。",
              "当前还没有做成用户自己在页面里点按钮、填店铺、立即完成 OAuth 绑定的最终流程。",
              shopify.publish_ready
                ? "当前执行层已经允许真实发布。"
                : "当前执行层还不是正式真实发布状态，所以这里不会假装已经能一键上架。",
              "也就是说，现在更接近“读取能力已接，用户自助绑定和真实发布还要继续收口”的阶段。",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/70">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button asChild><Link href={ROUTES.products}>去市场与商品页继续用</Link></Button>
          <Button asChild variant="secondary"><Link href={ROUTES.pricing}>去看套餐和充值</Link></Button>
          <Button asChild variant="outline"><Link href={ROUTES.settings}>回到账户中心</Link></Button>
        </div>
      </div>
    </XBorderLayout>
  );
}
