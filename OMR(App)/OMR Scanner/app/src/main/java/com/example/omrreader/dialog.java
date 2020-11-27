package com.example.omrreader;

import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

public class dialog extends AppCompatActivity {


    private Button alertButton;
    private TextView alertTextView;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.alert);
        alertButton = (Button) findViewById(R.id.AlertButton);
        //alertTextView = (TextView) findViewById(R.id.AlertTextView);



        alertButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View view) {
                AlertDialog.Builder builder = new AlertDialog.Builder(dialog.this);

                builder.setCancelable(true);
                builder.setTitle("Instructions! :)");
                builder.setMessage("1.\tUpload images in Step 1 only in .jpg,.jpeg or.png format. Any other format will not be accepted and an error message will flash. Also clicking the button without uploading any file will not be accepted.\n" +
                        "2.\tUpload answer key only in .csv format. Any other format or an empty value will not be accepted and an error message will be flashed.[Column Format - qno, answer, marks]\n" +
                        "3.\t Please remember to click the scan and upload buttons once you choose the files as clicking the buttons multiple times may lead to site failure.\n"
                       );


                builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialogInterface, int i) {
                       Intent intent = new Intent (dialog.this, MainActivity.class);

                       startActivity(intent);


                      //  web.loadUrl("http://40.87.52.33:5000/");
                    }
                    
                });
                builder.show();


            }
        });
    }


    }
