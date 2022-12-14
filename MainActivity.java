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

    private String[] serverUrls = new String[]{"https://scicd-h5-cdn.7road.net/index.js", "scicd-h5-cdn.7road.net"};//??????????????? https.__cdn-sq-h5-img.7road.net
//    private String[] serverUrls = new String[]{"https://cnd-sq-h5-img.7road.net/index.js", "cnd-sq-h5-img.7road.net"};//???????????????1 https.__cnd-sq-h5-img.7road.net
//    private String[] serverUrls = new String[]{"https://cnd-sq-h5-img.7road.net/index.js", "cnd-sq-h5-img.7road.net"};//???????????????2(iOS)
//    private String[] serverUrls = new String[]{"http://10.10.4.164/wartune/7road/index.js", "10.10.4.164"};//??????????????? 10.10.4.164_wartune_7road
//    private String[] serverUrls = new String[]{"http://10.10.19.120:8000/index.js", "10.10.19.120:8000"};//?????? 10.10.19.120.8000
//    private String[] serverUrls = new String[]{"https://ts1-h5.7road.net/index.js", "ts1-h5.7road.net/"};//ios?????????1
//    private String[] serverUrls = new String[]{"https://ts2-h5.7road.net/index.js", "ts2-h5.7road.net/"};//ios?????????2 https.__ts2-h5.7road.net
//    private String[] serverUrls = new String[]{"http://172.16.1.202/wartune/7road/index.js", "172.16.1.202"};//????????????????????? 172.16.1.202_wartune_7road
//    private String[] serverUrls = new String[]{"https://s5jr-h5-cdn.7road.net/index.js", "s5jr-h5.7road.net"};//????????????????????? https.__s5jr-h5-cdn.7road.net
//    private String[] serverUrls = new String[]{"https://sqh5-bmtest0001.wan.com/index.js", "sqh5-bmtest0001.wan.com"};//???????????????
//    private String[] serverUrls = new String[]{"https://s9999-h5-cdn.7road.net/index.js", "s9999-h5-cdn.7road.net"};//??????????????? https.__s9999-h5-cdn.7road.net

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        super.onCreate(savedInstanceState);

        setTheme(R.style.AppTheme);

        //??????????????????
        hideNavigationBar();
        //??????????????????
        Window window = this.getWindow();
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        //????????????????????????????????????
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

        //easyPermission????????????
        easyPermission = EasyPermission.build().mResult(new EasyPermissionResult() {
            @Override
            public void onPermissionsAccess(int requestCode) {
                super.onPermissionsAccess(requestCode);
                Log.i("TAG_Wartune", "???????????????");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                ExportJavaFunction.CallBackToJS(JSBridge.class,"checkPermission", 1);
            }

            @Override
            public void onPermissionsDismiss(int requestCode, @NonNull List<String> permissions) {
                super.onPermissionsDismiss(requestCode, permissions);
                Log.i("TAG_Wartune", permissions + " ????????????");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                ExportJavaFunction.CallBackToJS(JSBridge.class,"checkPermission", 0);
            }

            @Override
            public boolean onDismissAsk(int requestCode, @NonNull List<String> permissions) {
                Log.i("TAG_Wartune", permissions + " ??????????????????????????????????????????");
                MainActivity.this.autoLogin();
                if (isWifiFirst) {
                    showWifiTips(MainActivity.this);
                }
                return super.onDismissAsk(requestCode, permissions);//??????true?????????????????????????????????onPermissionsDismiss???
            }

            @Override
            public void openAppDetails() {
                //?????????????????????????????????????????????????????????????????????????????????????????????????????????onPermissionsAccess()
                super.openAppDetails();
            }
        });

        //????????????
        NotchFit.fit(this, NotchScreenType.FULL_SCREEN, new OnNotchCallBack() {
            @Override
            public void onNotchReady(NotchProperty notchProperty) {
                if (notchProperty.isNotchEnable()) {
                    statusBarHeight = notchProperty.getNotchWidth();
                    sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                    Log.i("TAG_Wartune", "???????????????" + notchProperty);
                } else {
                    float[] size = Utils.getScreenSize(MainActivity.this);
                    float sizeRate = size[0] / size[1];
                    if (sizeRate >= 2.1) {
                        statusBarHeight = 80;
                        sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                        Log.i("TAG_Wartune", "????????????" + sizeRate);
                    } else if (sizeRate >= 2.0) {
                        statusBarHeight = 70;
                        sreenRotation = notchProperty.getNotchPosition() == NotchPosition.LEFT ? 1 : 3;
                        Log.i("TAG_Wartune", "????????????" + sizeRate);
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
        pBuilder.setTitle("???????????????????????????????????????????????????").setMessage("????????????????????????????");
        // ????????????
        pBuilder.setPositiveButton("???", new DialogInterface.OnClickListener() {
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
        pBuilder.setNegativeButton("???", new DialogInterface.OnClickListener() {
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
        onWindowFocusChanged(true);//?????????home??????????????????????????????
        if (isLoad) mPlugin.game_plugin_onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        QianqiSDK.onPause();
        onWindowFocusChanged(false);//?????????home??????????????????????????????
        if (isLoad) mPlugin.game_plugin_onPause();
    }

    @Override
    protected void onStart() {
        super.onStart();
        QianqiSDK.onStart();
        onWindowFocusChanged(true);//?????????home??????????????????????????????
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
        //??????
        if (null != mLDNetPingService)
            this.mLDNetPingService.release();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        QianqiSDK.onActivityResult(requestCode, resultCode, data);
        //??????EasyPermissionHelper????????????(????????????????????????)
        EasyPermissionHelper.getInstance().onActivityResult(requestCode, resultCode, data);

        if (requestCode == 2) {
            // ????????????????????????
            Log.i("TAG_Wartune", "Result:" + data.toString());
            ContentResolver cr = this.getContentResolver();
            // ????????????????????????
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
                    Log.i("TAG_Wartune", "????????????:" + by);
                    JSBridge.callJS_getPhotoURI(String.valueOf(uri));
                } catch (Exception e) {
                    e.printStackTrace();
                }
//                iv_image.setImageURI(uri);
                Log.i("TAG_Wartune", "??????Uri:" + uri);
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
                    //code=0?????????js??????????????????????????????
                    JSBridge.callJS_showAlert(getString(R.string.is_exit_game), -1);
                } else {
                    //todo code!=0????????????????????????????????????????????????????????????????????????

                }
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        QianqiSDK.onRequestPermissionsResult(requestCode, permissions, grantResults);
        //??????EasyPermissionHelper????????????(??????????????????)
        EasyPermissionHelper.getInstance().onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    public void autoLogin() {
        if (!QianqiState.getInstance().isInit()) {
            return;
        }
        if (MainActivity.loginResult == null) {
            //????????????
            GameApplication.autoLogin(MainActivity.this, new GameLoginCallBack() {
                public void loginSuccess(LoginResult loginResult) {
                    String toJsonString = loginResult.toJsonString();
                    Log.i("TAG_Wartune", "?????????????????????" + toJsonString);
                    //????????????????????????????????????laya??????????????????laya????????????????????????laya????????????????????????andriod???????????????
                    MainActivity.loginResult = toJsonString;
                    //????????????????????????laya???????????????MainActivity.loginResult?????????????????????
                    JSBridge.nativeCallJs();
                }

                public void loginFail(int type, int errorCode, String errorMsg) {
                    Log.i("TAG_Wartune", "????????????????????? errorCode:" + errorCode + "  errorMsg:" + errorMsg);
                    MainActivity.loginResult = null;
                    JSBridge.nativeCallJs();
                    //remark ????????????
//                    GameApplication.showLogin(MainActivity.this, 0, null);
                }
            });
        }
    }

    public void initGameSDK() {
        if (!QianqiState.getInstance().isInit()) {
            GameApplication.initSDK(this, new GameInitCallBack() {
                public void initSuccess() {
                    Log.i("TAG_Wartune", "SDK??????????????????");
                    GameApplication.switchListener(MainActivity.this, null);
                    GameApplication.initVoice(MainActivity.this, null);
                    if (isFirstStart(MainActivity.this)) {
                        Log.i("TAG_Wartune", "???????????????app????????????????????????");
                        isWifiFirst = true;
                        MainActivity.this.requestPermissions();
                    } else {
                        Log.i("TAG_Wartune", "????????????app?????????????????????");
                        autoLogin();
                    }

                    String channelId = QianqiSDK.getConfigData(MainActivity.this).getChannelId();
                    mUpdateUrl = serverUrls[0].split("index.js")[0] + "appupdate/" + channelId + "/app-update.json";
                    Log.i("TAG_Wartune", "?????????????????????????????????" + mUpdateUrl);
                    XUpdate.newBuild(MainActivity.this)
                            .updateUrl(mUpdateUrl)
                            .updateParser(new CustomUpdateParser(MainActivity.this)) //???????????????????????????????????????
                            .updatePrompter(new CustomUpdatePrompter(MainActivity.this))
                            .update();
                }

                public void initFail(int errorCode, String errorMsg) {
                    Log.i("TAG_Wartune", "SDK???????????????");
                }

                public void exInfoBack(String str) {
                    Log.i("TAG_Wartune", "???????????????????????????????????????????????????");
                }

                public void localGoodsCallback(String str) {
                    Log.i("TAG_Wartune", "???????????????????????????????????????????????????GooglePay???AppStore???");
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
     * ??????????????????
     */
    public void requestPermissions() {
        this.runOnUiThread(new Runnable() {
            public void run() {
                //??????39????????????????????????????????????????????????
                if (ActivityCompat.shouldShowRequestPermissionRationale(MainActivity.this, Manifest.permission.READ_EXTERNAL_STORAGE)) {
                    Log.i("TAG_Wartune", "???????????????????????????????????????????????????????????????????????????");
                    MainActivity.this.autoLogin();
                    if (isWifiFirst) {
                        showWifiTips(MainActivity.this);
                    }
                    return;
                }
                //??????????????????
                PermissionAlertInfo alertInfo = new PermissionAlertInfo("????????????????????????", "??????????????????????????????????????????????????????????????????????????????????????????????????????????????????");
                easyPermission.mRequestCode(RC_CODE_PERMISSION)
                        .mAlertInfo(alertInfo)
                        .setAutoOpenAppDetails(false)
                        .mPerms(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE).requestPermission();
            }
        });
    }

    /**
     * ??????????????????
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
     * ???????????????????????????
     * <p>
     * ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????,??????????????????????????????????????????????????????
     *
     * @param context
     * @return
     */
    public static boolean isFirstStart(@NonNull Context context) {
        SharedPreferences preferences = context.getSharedPreferences("NB_FIRST_START", 0);
        Boolean isFirst = preferences.getBoolean("FIRST_START", true);
        if (isFirst) {// ?????????
            preferences.edit().putBoolean("FIRST_START", false).commit();
            return true;
        } else {
            return false;
        }
    }

    public void showWifiTips(@NonNull Context context) {

        ConnectivityManager connectivityManager = (ConnectivityManager) context
                .getSystemService(Context.CONNECTIVITY_SERVICE);//???????????????????????????
        NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();//???????????????????????????
        if (networkInfo.getType() != ConnectivityManager.TYPE_WIFI) {
            //??????WIFI???
            AlertDialog.Builder builder = new AlertDialog.Builder(context);
            builder.setTitle("??????")
                    .setMessage("?????????????????????????????????????????????WALN???????????????????????????WLAN?????????????????????????????????????????????")
                    .setPositiveButton("????????????", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
//                            if(networkInfo.getType()!=ConnectivityManager.TYPE_WIFI){
//                                showWifiTips(context);
//                            }
                        }
                    })
                    .setCancelable(false);

            builder.setNegativeButton("????????????", new DialogInterface.OnClickListener() {
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
