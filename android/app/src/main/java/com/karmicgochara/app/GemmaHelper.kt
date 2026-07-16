package com.karmicgochara.app

import com.google.ai.edge.litertlm.Message
import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.Content
import com.google.ai.edge.litertlm.Conversation
import android.util.Log
import java.lang.StringBuilder

object GemmaHelper {
    /**
     * Inférence SYNCHRONE via l'API LiteRT-LM officielle (sendMessage bloque
     * jusqu'à la réponse complète). Évite le piège sendMessageAsync().collect{}
     * dans un runBlocking (Flow streaming qui ne se termine pas → thread bloqué
     * → ANR + surchauffe GPU). Tourne déjà sur l'executor Capacitor (hors UI).
     */
    @JvmStatic
    fun generateSync(conversation: Conversation, prompt: String): String {
        return try {
            val message: Message = conversation.sendMessage(prompt)
            val sb = StringBuilder()
            for (content in message.contents.contents) {
                if (content is Content.Text) {
                    sb.append(content.text)
                }
            }
            sb.toString()
        } catch (e: Exception) {
            Log.e("GemmaHelper", "Error during generateSync", e)
            "Error: " + e.message
        }
    }
}
