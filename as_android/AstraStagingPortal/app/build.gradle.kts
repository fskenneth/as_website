plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization") version "2.0.0"
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.astrastaging.portal"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.astrastaging.portal"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        debug {
            // Tailscale IP for m4 — reachable from any network where the phone
            // has Tailscale active. Alternatives if this ever needs swapping:
            //   Emulator (no Tailscale): "http://10.0.2.2:5002"
            //   Same Wi-Fi as m4:        "http://192.168.2.<m4 LAN IP>:5002"
            //   MagicDNS (same tailnet): "http://kenneths-mac-mini-m4.taile1438a.ts.net:5002"
            buildConfigField("String", "API_BASE_URL", "\"http://100.114.47.80:5002\"")

            // DEV-ONLY auto-login: if non-empty, debug builds skip the login
            // screen and sign in with this token. Expires 2027-04-19. Delete
            // this line (or set to "") before any release / public build.
            buildConfigField(
                "String", "DEV_BYPASS_TOKEN",
                "\"dFF4hOUwq9s6nnOFzYBITC8OZ5_dyOqIBP8qzYHxyzU\""
            )

            // Plaintext HTTP allowed only in debug for local dev — controlled via
            // network_security_config.xml.
        }
        release {
            isMinifyEnabled = false
            buildConfigField("String", "API_BASE_URL", "\"https://portal.astrastaging.com\"")
            buildConfigField("String", "DEV_BYPASS_TOKEN", "\"\"")  // must stay empty in release
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.09.00")
    implementation(composeBom)
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.6")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.6")

    // Networking
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

    // Secure storage
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    // Image loading
    implementation("io.coil-kt:coil-compose:2.7.0")
    implementation("io.coil-kt:coil-video:2.7.0")

    // EXIF metadata — used to read orientation for thumbnail sizing.
    implementation("androidx.exifinterface:exifinterface:1.3.7")

    // CameraX — photo + video capture for the Consultation tab.
    val cameraxVersion = "1.3.4"
    implementation("androidx.camera:camera-core:$cameraxVersion")
    implementation("androidx.camera:camera-camera2:$cameraxVersion")
    implementation("androidx.camera:camera-lifecycle:$cameraxVersion")
    implementation("androidx.camera:camera-video:$cameraxVersion")
    implementation("androidx.camera:camera-view:$cameraxVersion")

    // Room — local queue for pending media captures.
    val roomVersion = "2.6.1"
    implementation("androidx.room:room-runtime:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")
    ksp("androidx.room:room-compiler:$roomVersion")

    // WorkManager — durable background uploads with Wi-Fi constraint.
    implementation("androidx.work:work-runtime-ktx:2.9.1")

    // DataStore — preferences for wifi-only toggle.
    implementation("androidx.datastore:datastore-preferences:1.1.1")

    debugImplementation("androidx.compose.ui:ui-tooling")
}
