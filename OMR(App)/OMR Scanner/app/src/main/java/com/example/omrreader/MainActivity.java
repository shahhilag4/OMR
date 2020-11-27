package com.example.omrreader;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.media.MediaScannerConnection;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.WindowManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import android.content.DialogInterface;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;


public class MainActivity extends AppCompatActivity {
    WebView web;
    private ValueCallback<Uri[]> mUploadMessage;
    private int GALLERY = 1, CAMERA = 2;
    public static final int REQUEST_ID_MULTIPLE_PERMISSIONS = 1;


    private Button alertButton;
    private TextView alertTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        web = findViewById(R.id.webview);
//        alertButton = (Button) findViewById(R.id.AlertButton);
//        alertTextView = (TextView)  findViewById(R.id.AlertTextView);
        WebSettings webSettings = web.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setAllowFileAccess(true);
        Callback callback=new Callback();
        web.setWebChromeClient(callback);
        webSettings.setAllowContentAccess(true);
  //      webSettings.setJavaScriptCanOpenWindowsAutomatically(true);
        //web.loadUrl("http://40.87.52.33:5000/");
        //requestMultiplePermissions();

        requestMultiplePermissions();

        ConnectivityManager connectivityManager=  (ConnectivityManager)getApplicationContext().getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo networkInfo=connectivityManager.getActiveNetworkInfo();
        if(networkInfo==null||!networkInfo.isConnected()||!networkInfo.isAvailable()){
            Dialog dialog=new Dialog(this);
            dialog.setContentView(R.layout.dialog);
            dialog.setCanceledOnTouchOutside(false);
            dialog.getWindow().setLayout(WindowManager.LayoutParams.WRAP_CONTENT,WindowManager.LayoutParams.WRAP_CONTENT);
            dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            dialog.getWindow().getAttributes().windowAnimations= android.R.style.Animation_Dialog;
            dialog.show();
        }
        else {
            web.loadUrl("http://40.87.52.33:5000/");
        }


    }





    private void showPictureDialog() {
        AlertDialog.Builder pictureDialog = new AlertDialog.Builder(this);
        pictureDialog.setCancelable(true);
        pictureDialog.setOnCancelListener(new DialogInterface.OnCancelListener() {
            @Override
            public void onCancel(DialogInterface dialogInterface) {
                mUploadMessage.onReceiveValue(null);
                mUploadMessage = null;
                Log.d("tmpsrt","testcancel");
            }
        });







        pictureDialog.setTitle("Select an option");
        String[] pictureDialogItems = {"Filemanager", "Camera"};
        pictureDialog.setItems(pictureDialogItems,
                new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        switch (which) {
                            case 0:
                                showFileChooser();
                                break;
                            case 1:
                                takePhotoFromCamera();
                                break;
                        }
                    }
                });
        AlertDialog alert = pictureDialog.create();
        alert.show();
    }

    private void showFileChooser(){
        Intent intent=new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType("*/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
       intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);
      // startActivityForResult(Intent.createChooser(intent, "Image Browser"), FILECHOOSER_RESULTCODE);

        try {
            startActivityForResult(
                    Intent.createChooser(intent,"Select a file to upload"),
                    GALLERY);
        }
        catch (android.content.ActivityNotFoundException ec){
            Toast.makeText(this,"Please install a file manager",
                    Toast.LENGTH_SHORT).show();
        }



    }

    private void takePhotoFromCamera() {
        Intent intent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(intent, CAMERA);
    }

    public String saveImage(Bitmap myBitmap) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        myBitmap.compress(Bitmap.CompressFormat.JPEG, 90, bytes);
        File temp=
                Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM);
        if (!temp.exists()) {  // have the object build the directory structure, if needed.
            temp.mkdirs();
        }

        try {
            File f = new File(temp, Calendar.getInstance().getTimeInMillis() + ".jpg");
            f.createNewFile();
            FileOutputStream fo = new FileOutputStream(f);
            fo.write(bytes.toByteArray());
            MediaScannerConnection.scanFile(this,
                    new String[]{f.getPath()},
                    new String[]{"image/jpeg"}, null);
            fo.close();
            Log.d("TAG", "File Saved::---&gt;" + f.getAbsolutePath());

            return f.getAbsolutePath();
        } catch (IOException e1) {
            e1.printStackTrace();
        }
        return "";
    }

    private class Callback extends WebChromeClient {
        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {

            if (mUploadMessage!=null)
                mUploadMessage.onReceiveValue(null);
            mUploadMessage=filePathCallback;
            showPictureDialog();
       //     showFileChooser();
            return true;
        }

    }

    private void requestMultiplePermissions() {
            int storageR = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE);
            int storageW = ContextCompat.checkSelfPermission(this, android.Manifest.permission.WRITE_EXTERNAL_STORAGE);
            int camera = ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA);
            Intent intent = new Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS" ) ;

            List<String> listPermissionsNeeded = new ArrayList<>();

            if (storageR != PackageManager.PERMISSION_GRANTED) {
                listPermissionsNeeded.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            }
            if (storageW != PackageManager.PERMISSION_GRANTED) {
                listPermissionsNeeded.add(android.Manifest.permission.WRITE_EXTERNAL_STORAGE);
            }

            if (camera != PackageManager.PERMISSION_GRANTED) {
            listPermissionsNeeded.add(Manifest.permission.CAMERA);
            }

            if (!listPermissionsNeeded.isEmpty())
            {
                ActivityCompat.requestPermissions(this,listPermissionsNeeded.toArray
                        (new String[listPermissionsNeeded.size()]),REQUEST_ID_MULTIPLE_PERMISSIONS);
                Toast.makeText(getApplicationContext(),"Please Grant All Permissions First",Toast.LENGTH_SHORT).show();
            }
    }

    public Uri getImageUri(Context inContext, Bitmap inImage) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        inImage.compress(Bitmap.CompressFormat.JPEG, 100, bytes);
        String path = MediaStore.Images.Media.insertImage(inContext.getContentResolver(), inImage, "Title", null);
        return Uri.parse(path);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);

        ArrayList<Uri> results = new ArrayList<>();
        Uri[] files = null;
        if (resultCode == RESULT_OK) {
            if (requestCode == GALLERY) {
                if(null != intent) { // checking empty selection
                    if (null != intent.getClipData()) { // checking multiple selection or not
                        for(int i = 0; i < intent.getClipData().getItemCount(); i++) {
                            Uri uri = intent.getClipData().getItemAt(i).getUri();
                            results.add(uri);
                            files =results.toArray(new Uri[results.size()]);
                        }
                    } else {
                        Uri uri = intent.getData();
                        results.add(uri);
                        files =results.toArray(new Uri[results.size()]);
                    }
                    mUploadMessage.onReceiveValue(files);
                    mUploadMessage=null;
                }
            }

            else if (requestCode == CAMERA) {
                Bitmap img = (Bitmap) intent.getExtras().get("data");
                Uri uri = getImageUri(getApplicationContext(), img);
                results.add(uri);
                files =results.toArray(new Uri[results.size()]);
                mUploadMessage.onReceiveValue(files);
                mUploadMessage=null;
            }
        }

        else{
            mUploadMessage.onReceiveValue(null);
            mUploadMessage=null;
        }
    }

}
