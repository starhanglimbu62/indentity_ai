import React from 'react'

export default function FileUploader({ onFile }: { onFile: (f: File) => void }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 transition hover:border-indigo-300 hover:bg-indigo-50">
      <label className="block cursor-pointer text-sm font-semibold text-slate-700">
        Choose a document
        <input type="file" onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f) }} className="mt-2 block w-full cursor-pointer text-sm font-normal text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:font-semibold file:text-white" />
      </label>
    </div>
  )
}
