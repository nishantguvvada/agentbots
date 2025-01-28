"use client"

import axios from "axios";
import { useEffect, useState } from "react"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL

export const Table = () => {
    const [notes, setNotes] = useState([]);
    useEffect(() => {
        const getNotes = async () => {
            try {
                const response = await axios.get(BACKEND_URL);
                setNotes(response.data.response);
            } catch(err) {
                console.log(err);
            }
        }
        getNotes();
    }, []);
    return (
        <>
            {notes.length === 0 ? <div className="w-full h-full flex justify-center items-center"><h1 className="text-center max-w-2xl mb-4 text-4xl font-extrabold tracking-tight leading-none md:text-5xl xl:text-6xl">No notes created!</h1></div> :
            <div className="w-full overflow-x-auto shadow-md sm:rounded-lg">
                <table className="w-full text-sm text-left rtl:text-right text-gray-500">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3">
                                #
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Note
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {notes.map((note, i) => { return (
                            <tr key={i} className="bg-white border-b border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600">
                                <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                                    {i+1}
                                </th>
                                <td className="px-6 py-4">
                                    {note.title}
                                </td>
                                <td className="px-6 py-4">
                                    <a href="#" className="font-medium text-blue-600 hover:underline">View</a>
                                </td>
                            </tr>
                        )})}
                    </tbody>
                </table>
            </div>
            }
        </>
    )
}