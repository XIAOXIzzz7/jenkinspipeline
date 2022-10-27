package demo;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.AlertDialog;
import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.ContentResolver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.core.app.ActivityCompat;

import com.qianqi.integrate.QianqiSDK;
import com.qianqi.integrate.QianqiState;
import com.qianqi.integrate.bean.LoginResult;
import com.qianqi.integrate.callback.BackPressedCallBack;
import com.qianqi.integrate.callback.GameInitCallBack;
import com.qianqi.integrate.callback.GameLoginCallBack;
import com.road7.sqh5.R;
import com.wcl.notchfit.NotchFit;
import com.wcl.notchfit.args.NotchPosition;
import com.wcl.notchfit.args.NotchProperty;
import com.wcl.notchfit.args.NotchScreenType;
import com.wcl.notchfit.core.OnNotchCallBack;
import com.xuexiang.xupdate.XUpdate;
import com.zyq.easypermission.EasyPermission;
import com.zyq.easypermission.EasyPermissionHelper;
import com.zyq.easypermission.EasyPermissionResult;
import com.zyq.easypermission.bean.PermissionAlertInfo;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.List;

import layaair.game.IMarket.IPlugin;
import layaair.game.IMarket.IPluginRuntimeProxy;
import layaair.game.Market.GameEngine;
import layaair.game.browser.ExportJavaFunction;
import layaair.game.config.config;
import update.CustomUpdateParser;
import update.CustomUpdatePrompter;


public class MainActivity extends Activity {
    public static final int AR_CHECK_UPDATE = 1;
    public static boolean layaLoadFinished = false;
    private IPlugin mPlugin = null;
    private IPluginRuntimeProxy mProxy = null;
    boolean isLoad = false;
    boolean isExit = false;
    public static SplashDialog mSplashDialog;
    public static String loginResult;
    public static int statusBarHeight;
    public static int sreenRotation;
    private PingNetManager mLDNetPingService;
    public EasyPermission easyPermission;
    protected static final int RC_CODE_PERMISSION = 1024;
    private boolean isWifiFirst = false;
    private String mUpdateUrl = "";//https://cdn-sq-h5-img.7road.net/appupdate/20350/app-update.json";

    private String[] serverUrls = new String[]{"https://scicd-h5-cdn.7road.net/index.js", "scicd-h5-cdn.7road.net"};//外网正式服 https.__cdn-sq-h5-img.7road.net
//    private String[] serverUrls = new String[]{"https://cnd-sq-h5-img.7road.net/index.js", "cnd-sq-h5-img.7road.net"};//外网测试服1 https.__cnd-sq-h5-img.7road.net
//    private String[] serverUrls = new String[]{"https://cnd-sq-h5-img.7road.net/index.js", "cnd-sq-h5-img.7road.net"};//外网测试服2(iOS)
//    private String[] serverUrls = new String[]{"http://10.10.4.164/wartune/7road/index.js", "10.10.4.164"};//内网测试服 10.10.4.164_wartune_7road
//    private String[] serverUrls = new String[]{"http://10.10.19.120:8000/index.js", "10.10.19.120:8000"};//本地 10.10.19.120.8000
//    private String[] serverUrls = new String[]{"https://ts1-h5.7road.net/index.js", "ts1-h5.7road.net/"};//ios测试服1
//    private String[] serverUrls = new String[]{"https://ts2-h5.7road.net/index.js", "ts2-h5.7road.net/"};//ios测试服2 https.__ts2-h5.7road.net
//    private String[] serverUrls = new String[]{"http://172.16.1.202/wartune/7road/index.js", "172.16.1.202"};//国内内网测试服 172.16.1.202_wartune_7road
//    private String[] serverUrls = new String[]{"https://s5jr-h5-cdn.7road.net/index.js", "s5jr-h5.7road.net"};//国内兼容测试服 https.__s5jr-h5-cdn.7road.net
//    private String[] serverUrls = new String[]{"https://sqh5-bmtest0001.wan.com/index.js", "sqh5-bmtest0001.wan.com"};//北美测试服
//    private String[] serverUrls = new String[]{"https://s9999-h5-cdn.7road.net/index.js", "s9999-h5-cdn.7road.net"};//性能测试服 https.__s9999-h5-cdn.7road.net

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        super.onCreate(savedInstanceState);

        setTheme(R.style.AppTheme);

        //隐藏虚拟按键
        hideNavigationBar();
        //设置屏幕常亮
        Window window = this.getWindow();
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        //设置为全屏（隐藏状态栏）
//        window.requestFeature(Window.FEATURE_NO_TITLE);
        window.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            WindowManager.LayoutParams lp = window.getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            window.setAttributes(lp);
            View decorView = window.getDecorView();
            int systemUiVisibility = decorView.getSystemUiVisibility();
            int flags = View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_FULLSCREEN;
            systemUiVisibility |= flags;
            window.getDecorView().setSystemUiVisibility(systemUiVisibility);
        }

        //SDK
        QianqiSDK.onCreate(this, savedInstanceState);

        JSBridge.mMainActivity = this;
        mSplashDialog = new SplashDialog(this);
        mSplashDialog.showSplash();
        initEngine();

        //ping
        this.mLDNetPingService = new PingNetManager(this.serverUrls[1]);
        this.mLDNetPingService.startPing();

        //easyPermission权限处理
        easyPermission = EasyPermission.build().mResult(new EasyPermissionResult() {
            @Override
            public void onPermissionsAccess(int requestCode) {
                super.onPermissionsAccess(requestCode);
                Log.i("TAG_Wartune", "权限已通过");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                ExportJavaFunction.CallBackToJS(JSBridge.class,"checkPermission", 1);
            }

            @Override
            public void onPermissionsDismiss(int requestCode, @NonNull List<String> permissions) {
                super.onPermissionsDismiss(requestCode, permissions);
                Log.i("TAG_Wartune", permissions + " 被拒绝了");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                ExportJavaFunction.CallBackToJS(JSBridge.class,"checkPermission", 0);
            }

            @Override
            public boolean onDismissAsk(int requestCode, @NonNull List<String> permissions) {
                Log.i("TAG_Wartune", permissions + " 被禁止了，需要向用户说明情况");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                return super.onDismissAsk(requestCode, permissions);//这里true表示拦截处理，不再回调onPermissionsDismiss；
            }

            @Override
            public void openAppDetails() {
                //弹出默认的权限详情设置提示弹出框，在设置页完成允许操作后，会自动回调到onPermissionsAccess()
                super.openAppDetails();
            }
        });

        //刘海适配
        NotchFit.fit(this, NotchScreenType.FULL_SCREEN, new OnNotchCallBack() {
            @Override
            public void onNotchReady(NotchProperty notchProperty) {
                if (notchProperty.isNotchEnable()) {
                    statusBarHeight = notchProperty.getNotchWidth();
                    sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                    Log.i("TAG_Wartune", "刘海信息：" + notchProperty);
                } else {
                    float[] size = Utils.getScreenSize(MainActivity.this);
                    float sizeRate = size[0] / size[1];
                    if (sizeRate >= 2.1) {
                        statusBarHeight = 80;
                        sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                        Log.i("TAG_Wartune", "宽高比：" + sizeRate);
                    } else if (sizeRate >= 2.0) {
                        statusBarHeight = 70;
                        sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                        Log.i("TAG_Wartune", "宽高比：" + sizeRate);
                    }
                }
                if (layaLoadFinished) {
//                    statusBarHeight = Math.min(statusBarHeight, 80);
                    JSBridge.callJS_getNoSafeAreaHeight(statusBarHeight, statusBarHeight, sreenRotation);
                }
            }
        });
    }

    public void initEngine() {
        mProxy = new RuntimeProxy(this);
        mPlugin = new GameEngine(this);
        mPlugin.game_plugin_set_runtime_proxy(mProxy);
        mPlugin.game_plugin_set_option("localize", "false");
        mPlugin.game_plugin_set_option("gameUrl", this.serverUrls[0]);
        mPlugin.game_plugin_init(3);
        View gameView = mPlugin.game_plugin_get_view();
        this.setContentView(gameView);
        isLoad = true;
    }

    public boolean isOpenNetwork(Context context) {
        if (!config.GetInstance().m_bCheckNetwork)
            return true;
        ConnectivityManager connManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        return connManager.getActiveNetworkInfo() != null && (connManager.getActiveNetworkInfo().isAvailable() && connManager.getActiveNetworkInfo().isConnected());
    }

    public void settingNetwork(final Context context, final int p_nType) {
        AlertDialog.Builder pBuilder = new AlertDialog.Builder(context);
        pBuilder.setTitle("连接失败，请检查网络或与开发商联系").setMessage("是否对网络进行设置?");
        // 退出按钮
        pBuilder.setPositiveButton("是", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface p_pDialog, int arg1) {
                Intent intent;
                try {
                    String sdkVersion = android.os.Build.VERSION.SDK;
                    if (Integer.valueOf(sdkVersion) > 10) {
                        intent = new Intent(
                                android.provider.Settings.ACTION_WIRELESS_SETTINGS);
                    } else {
                        intent = new Intent();
                        ComponentName comp = new ComponentName(
                                "com.android.settings",
                                "com.android.settings.WirelessSettings");
                        intent.setComponent(comp);
                        intent.setAction("android.intent.action.VIEW");
                    }
                    ((Activity) context).startActivityForResult(intent, p_nType);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        pBuilder.setNegativeButton("否", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                dialog.cancel();
                ((Activity) context).finish();
            }
        });
        AlertDialog alertdlg = pBuilder.create();
        alertdlg.setCanceledOnTouchOutside(false);
        alertdlg.show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        QianqiSDK.onResume();
        onWindowFocusChanged(true);//解决按home键切换到后台游戏黑屏
        if (isLoad) mPlugin.game_plugin_onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        QianqiSDK.onPause();
        onWindowFocusChanged(false);//解决按home键切换到后台游戏黑屏
        if (isLoad) mPlugin.game_plugin_onPause();
    }

    @Override
    protected void onStart() {
        super.onStart();
        QianqiSDK.onStart();
        onWindowFocusChanged(true);//解决按home键切换到后台游戏黑屏
        if (isLoad) mPlugin.game_plugin_onResume();
    }

    @Override
    protected void onRestart() {
        super.onRestart();
        QianqiSDK.onRestart();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        QianqiSDK.onNewIntent(intent);
    }

    @Override
    protected void onStop() {
        super.onStop();
        QianqiSDK.onStop();
        if (isLoad) mPlugin.game_plugin_onStop();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        QianqiSDK.onDestroy();
        if (isLoad) mPlugin.game_plugin_onDestory();
        //释放
        if (null != mLDNetPingService)
            this.mLDNetPingService.release();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        QianqiSDK.onActivityResult(requestCode, resultCode, data);
        //使用EasyPermissionHelper注入回调(系统设置返回使用)
        EasyPermissionHelper.getInstance().onActivityResult(requestCode, resultCode, data);

        if (requestCode == 2) {
            // 从相册返回的数据
            Log.i("TAG_Wartune", "Result:" + data.toString());
            ContentResolver cr = this.getContentResolver();
            // 得到图片的全路径
            Uri uri = data.getData();
            if (uri != null) {
                try {
                    InputStream is = cr.openInputStream(uri);
                    Bitmap bitmap = BitmapFactory.decodeStream(is);
                    ByteArrayOutputStream out = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out);
                    byte[] by;
                    out.flush();
                    out.close();
                    by = out.toByteArray();
                    Log.i("TAG_Wartune", "图片数据:" + by);
                    JSBridge.callJS_getPhotoURI(String.valueOf(uri));
                } catch (Exception e) {
                    e.printStackTrace();
                }
//                iv_image.setImageURI(uri);
                Log.i("TAG_Wartune", "图片Uri:" + uri);
            }
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
//            MainActivity.this.requestPermissions();
//            JSBridge.reload();
            onBackPressed();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        QianqiSDK.backPressed(new BackPressedCallBack() {
            public void backPressedCallback(int code) {
                if (code == 0) {
                    //code=0时展示js自身的确认退出界面；
                    JSBridge.callJS_showAlert(getString(R.string.is_exit_game), -1);
                } else {
                    //todo code!=0展示渠道确认退出界面，游戏不要再展示确认退出界面

                }
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        QianqiSDK.onRequestPermissionsResult(requestCode, permissions, grantResults);
        //使用EasyPermissionHelper注入回调(授权弹窗回调)
        EasyPermissionHelper.getInstance().onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    public void autoLogin() {
        if (!QianqiState.getInstance().isInit()) {
            return;
        }
        if (MainActivity.loginResult == null) {
            //自动登录
            GameApplication.autoLogin(MainActivity.this, new GameLoginCallBack() {
                public void loginSuccess(LoginResult loginResult) {
                    String toJsonString = loginResult.toJsonString();
                    Log.i("TAG_Wartune", "自动登录成功！" + toJsonString);
                    //把值先存起来不要直接发给laya端，因为此时laya端还未加载完，等laya端加载完主动来调andriod端再给数据
                    MainActivity.loginResult = toJsonString;
                    //主动发一下，防止laya端加载完了MainActivity.loginResult还没有值的情况
                    JSBridge.nativeCallJs();
                }

                public void loginFail(int type, int errorCode, String errorMsg) {
                    Log.i("TAG_Wartune", "自动登录失败！ errorCode:" + errorCode + "  errorMsg:" + errorMsg);
                    MainActivity.loginResult = null;
                    JSBridge.nativeCallJs();
                    //remark 暂时屏蔽
//                    GameApplication.showLogin(MainActivity.this, 0, null);
                }
            });
        }
    }

    public void initGameSDK() {
        if (!QianqiState.getInstance().isInit()) {
            GameApplication.initSDK(this, new GameInitCallBack() {
                public void initSuccess() {
                    Log.i("TAG_Wartune", "SDK初始化成功！");
                    GameApplication.switchListener(MainActivity.this, null);
                    GameApplication.initVoice(MainActivity.this, null);
                    if (isFirstStart(MainActivity.this)) {
                        Log.i("TAG_Wartune", "第一次启动app，开始请求权限！");
                        isWifiFirst = true;
                        MainActivity.this.requestPermissions();
                    } else {
                        Log.i("TAG_Wartune", "之后启动app，直接自动登录");
                        autoLogin();
                    }

                    String channelId = QianqiSDK.getConfigData(MainActivity.this).getChannelId();
                    mUpdateUrl = serverUrls[0].split("index.js")[0] + "appupdate/" + channelId + "/app-update.json";
                    Log.i("TAG_Wartune", "当前强更配置文件地址：" + mUpdateUrl);
                    XUpdate.newBuild(MainActivity.this)
                            .updateUrl(mUpdateUrl)
                            .updateParser(new CustomUpdateParser(MainActivity.this)) //设置自定义的版本更新解析器
                            .updatePrompter(new CustomUpdatePrompter(MainActivity.this))
                            .update();
                }

                public void initFail(int errorCode, String errorMsg) {
                    Log.i("TAG_Wartune", "SDK初始化失败");
                }

                public void exInfoBack(String str) {
                    Log.i("TAG_Wartune", "启动应用时返回邀请进入房间等的信息");
                }

                public void localGoodsCallback(String str) {
                    Log.i("TAG_Wartune", "启动应用时返回本地化商品信息（比如GooglePay或AppStore）");
                }
            });
        }
    }

    @Override
    protected void attachBaseContext(Context newBase) {
        super.attachBaseContext(newBase);
        QianqiSDK.activityAttachBaseContext(newBase);
    }

    @Override
    public void onConfigurationChanged(@NonNull Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        QianqiSDK.activityOnConfigurationChanged(newConfig);
    }
    //------------------------------------------------------------------------------

    /**
     * 申请权限访问
     */
    public void requestPermissions() {
        this.runOnUiThread(new Runnable() {
            public void run() {
                //解决39渠道方和母包重复弹权限申请的问题
                if (ActivityCompat.shouldShowRequestPermissionRationale(MainActivity.this, Manifest.permission.READ_EXTERNAL_STORAGE)) {
                    Log.i("TAG_Wartune", "已经请求了权限，用户选择了拒绝权限，但不是永久拒绝");
                    MainActivity.this.autoLogin();
                    if (isWifiFirst) {
                        showWifiTips(MainActivity.this);
                    }
                    return;
                }
                //设置权限描述
                PermissionAlertInfo alertInfo = new PermissionAlertInfo("设备权限使用说明", "需要申请存储和设备信息权限，用于存储游戏数据、进行信息推送和安全保障等功能。");
                easyPermission.mRequestCode(RC_CODE_PERMISSION)
                        .mAlertInfo(alertInfo)
                        .setAutoOpenAppDetails(false)
                        .mPerms(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE).requestPermission();
            }
        });
    }

    /**
     * 隐藏虚拟按键
     */
    public void hideNavigationBar() {
        int uiFlags = View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION // hide nav bar
                | View.SYSTEM_UI_FLAG_FULLSCREEN; // hide status bar

        if (android.os.Build.VERSION.SDK_INT >= 21) {
            uiFlags |= 0x00001000;  //SYSTEM_UI_FLAG_IMMERSIVE_STICKY: hide navigation bars - compatibility: building API level is lower thatn 19, use magic number directly for higher API target level
        } else {
            uiFlags |= View.SYSTEM_UI_FLAG_LOW_PROFILE;
        }
        getWindow().getDecorView().setSystemUiVisibility(uiFlags);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideNavigationBar();
        }
    }

    public void restartApplication() {
        Intent mStartActivity = new Intent(this, MainActivity.class);
        int mPendingIntentId = 123456;
        PendingIntent mPendingIntent = PendingIntent.getActivity(this, mPendingIntentId, mStartActivity, PendingIntent.FLAG_CANCEL_CURRENT);
        AlarmManager mgr = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        mgr.set(AlarmManager.RTC, System.currentTimeMillis() + 100, mPendingIntent);
        System.exit(0);
    }

    protected void mToast(CharSequence msg) {
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
    }

    /**
     * 判断是否是首次启动
     * <p>
     * 此方法启动调用第一次是准确值，如果在一次启动中多次调用，即使是首次启动，第二次调用也会变成非首次启动，若需要多次获取，可以赋新值使用,每次启动只能调用此方法一次，赋值获取
     *
     * @param context
     * @return
     */
    public static boolean isFirstStart(@NonNull Context context) {
        SharedPreferences preferences = context.getSharedPreferences("NB_FIRST_START", 0);
        Boolean isFirst = preferences.getBoolean("FIRST_START", true);
        if (isFirst) {// 第一次
            preferences.edit().putBoolean("FIRST_START", false).commit();
            return true;
        } else {
            return false;
        }
    }

    public void showWifiTips(@NonNull Context context) {

        ConnectivityManager connectivityManager = (ConnectivityManager) context
                .getSystemService(Context.CONNECTIVITY_SERVICE);//获取系统的连接服务
        NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();//获取网络的连接情况
        if (networkInfo.getType() != ConnectivityManager.TYPE_WIFI) {
            //判断WIFI网
            AlertDialog.Builder builder = new AlertDialog.Builder(context);
            builder.setTitle("提示")
                    .setMessage("部分游戏资源需要更新，推荐使用WALN下载。检测到您当前WLAN还未打开或连接，是否继续下载？")
                    .setPositiveButton("继续下载", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
//                            if(networkInfo.getType()!=ConnectivityManager.TYPE_WIFI){
//                                showWifiTips(context);
//                            }
                        }
                    })
                    .setCancelable(false);

            builder.setNegativeButton("以后再说", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    System.exit(0);
                }
            });

            AlertDialog alertDialog = builder.create();
            alertDialog.show();
        }
    }

}
