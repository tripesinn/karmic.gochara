package com.karmicgochara.app

import com.google.ai.edge.litertlm.Message
import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.Content
import com.google.ai.edge.litertlm.Conversation
import android.util.Log
import kotlinx.coroutines.runBlocking
import java.lang.StringBuilder

object GemmaHelper {
    @JvmStatic
    fun generateSync(conversation: Conversation, prompt: String): String = runBlocking {
        val sb = StringBuilder()
        try {
            conversation.sendMessageAsync(prompt).collect { message ->
                val contentsList = message.contents.contents
                for (content in contentsList) {
                    if (content is Content.Text) {
                        sb.append(content.text)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("GemmaHelper", "Error during generateSync", e)
            return@runBlocking "Error: " + e.message
        }
        sb.toString()
    }
}
