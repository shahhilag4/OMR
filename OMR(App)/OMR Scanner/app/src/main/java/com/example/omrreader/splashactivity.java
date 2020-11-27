package com.example.omrreader;

import android.content.Intent;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

public  class splashactivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.splash_activity);
        Thread thread=new Thread(){
            public  void run(){
                try {
                    sleep(2000);
                }
                catch (Exception e){
                    e.printStackTrace();
                }
             finally {
                    Intent intent= new Intent(splashactivity.this, dialog.class);
                    startActivity(intent);
                }


            }
        };thread.start();
    }



}
