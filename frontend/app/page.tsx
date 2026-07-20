import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { getCurrentUser, isAuthError, isBannedError, isQuotaError } from "@/lib/api-gateway";
import { NewDashboard } from "@/modules/dashboard/new-dashboard";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { PublicHomeShell } from "@/components/marketing/public-home-shell";
import { AccountBannedPanel } from "@/components/auth/account-banned-panel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, StatusAlert } from "@/design-system/components";

export default async function HomePage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";

  if (!token) {
    return <PublicHomeShell lang={lang} />;
  }

  try {
    await getCurrentUser(token);
  } catch (error) {
    if (isBannedError(error)) {
      return <AccountBannedPanel lang={lang} />;
    }
    if (isAuthError(error)) {
      return <PublicHomeShell lang={lang} />;
    }
    throw error;
  }

  try {
    return await NewDashboard({ token, lang });
  } catch (error) {
    if (isBannedError(error)) {
      return <AccountBannedPanel lang={lang} />;
    }
    if (isAuthError(error)) {
      return <PublicHomeShell lang={lang} />;
    }
    if (isQuotaError(error)) {
      return (
        <XBorderLayout lang={lang} activePath="home">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardContent className="p-6">
              <StatusAlert
                status="warning"
                message="今天的可用接口次数已经用完了。首页先给你正常打开，但实时数据今天先不再继续请求。你可以明天再刷新，或者先去看已经入库的商品和历史分析。"
              />
            </CardContent>
          </Card>
        </XBorderLayout>
      );
    }
    throw error;
  }
}
