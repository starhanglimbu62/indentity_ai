import React from 'react'

export default function FileUploader({ onFile }: { onFile: (f: File) => void }) {
  return (
    <div>
      <input type="file" onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f) }} />
    </div>
  )
}
