import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, Button, KpiTile, SectionIntro } from "@/design-system/components";
import { StoreLinkGate } from "@/components/settings/store-link-gate";
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
  const nextSteps = [
    {
      title: shopify.store_base_url_configured ? "店铺地址参数已到位" : "先补店铺地址参数",
      desc: shopify.store_base_url_configured
        ? "系统已经拿到店铺地址参数，下一步主要看能不能继续读商品、继续执行。"
        : "当前第一步还没补齐，所以这里不会假装你已经能开始读店铺。",
    },
    {
      title: shopify.admin_read_ready ? "已经能读真实商品" : "还不能读真实商品",
      desc: shopify.admin_read_ready
        ? "你现在可以把 Shopify 作为真实参考商品源，继续往市场和商品页走。"
        : "现在还不能从 Shopify 读真实商品，所以这页只告诉你真实状态。",
    },
    {
      title: shopify.oauth_status === "reserved" ? "自助绑定流程还没做完" : "绑定状态已更新",
      desc: shopify.oauth_status === "reserved"
        ? "当前只是把 OAuth 结构预留了，还没有做到你自己点一下就完成绑定。"
        : `当前绑定状态：${shopify.oauth_status}`,
    },
    {
      title: shopify.publish_ready ? "发布链路已打开" : "发布链路还没正式放开",
      desc: shopify.publish_ready
        ? "你可以继续去利润页和执行页看真实上架动作。"
        : "现在不会假装已经能一键上架，发布能力还要继续收口。",
    },
  ];

  const useActions = [
    shopify.admin_read_ready
      ? {
          title: "继续做市场分析",
          desc: "既然店铺读取已经打开，就继续去看市场、趋势和商品机会。",
          href: ROUTES.insights,
          label: "去市场智能页",
        }
      : {
          title: "先看套餐和能力",
          desc: "当前没有自助绑定完成链路，先确认套餐和权限是不是够用。",
          href: ROUTES.pricing,
          label: "去套餐页",
        },
    {
      title: "继续做商品筛选",
      desc: "不管店铺绑定走到哪一步，你都可以继续看商品机会和供应链。",
      href: ROUTES.products,
      label: "去商品机会页",
    },
    {
      title: shopify.publish_ready ? "继续看执行发布" : "先看利润和上架判断",
      desc: shopify.publish_ready
        ? "当前执行层已经开到发布这一步，可以继续看执行记录。"
        : "当前更适合先完成利润判断，再决定后面什么时候发。",
      href: shopify.publish_ready ? ROUTES.actionLaunchQueue : ROUTES.actionProfit,
      label: shopify.publish_ready ? "去执行页" : "去利润页",
    },
  ];

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商航AI · Shopify Center"
              title="店铺绑定"
              description="这个页面现在不再放空话，直接告诉你 Shopify 到底已经接到哪一步：真实读取、用户自助绑定、真实发布，分别到什么状态。"
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <KpiTile label="店铺状态" value={shopify.status_text} hint="先看当前是不是已接通" />
              <KpiTile label="真实读取" value={shopify.admin_read_ready ? "已打开" : "未打开"} hint="能不能读取商品和订单数据" />
              <KpiTile label="绑定状态" value={shopify.oauth_status === "reserved" ? "待收口" : shopify.oauth_status} hint="用户能不能自己完成连接" />
              <KpiTile label="发布状态" value={shopify.publish_ready ? "可继续验证" : "未正式放开"} hint="这决定后面是否能继续执行发布" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>你现在下一步该怎么走</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {nextSteps.map((item) => (
              <div key={item.title} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/70">
                <div className="font-medium text-white">{item.title}</div>
                <div className="mt-2 leading-7 text-white/60">{item.desc}</div>
              </div>
            ))}
          </CardContent>
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

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前可继续使用的动作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {useActions.map((item) => (
                <div key={item.title} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                  <div className="text-base font-medium text-white">{item.title}</div>
                  <div className="mt-2 text-sm leading-7 text-white/60">{item.desc}</div>
                  <div className="mt-4">
                    <Button asChild>
                      <Link href={item.href}>{item.label}</Link>
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>现在不能假装完成的部分</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/70">
                当前没有做成“你自己填店铺信息后，马上绑定成功”的最终自助流程。
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/70">
                如果发布能力还没放开，这页不会假装你已经可以正式一键上架。
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/70">
                所以这页现在更像“真实状态页 + 下一步入口页”，不是假装全闭环的炫技页。
              </div>
              <div className="pt-2">
                <StoreLinkGate />
              </div>
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
          <Button asChild variant="secondary"><Link href={ROUTES.actionLaunchQueue}>去执行页看发布状态</Link></Button>
          <Button asChild variant="outline"><Link href={ROUTES.settings}>回到账户中心</Link></Button>
        </div>
      </div>
    </XBorderLayout>
  );
}
